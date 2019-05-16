from bottle import get, post, template, request, abort
import requests
import os, sys, json, atexit, socket, zipfile, io
from base64 import standard_b64encode, standard_b64decode
from threading import Thread
from functools import reduce
from operator import add
try:
    from nacl.secret import SecretBox
    from nacl.utils import random
except ImportError:
    from libnacl.secret import SecretBox
    from libnacl import randombytes as random
from hkdf import hkdf_extract, hkdf_expand
import appdirs
from boundery import osal
from boundery.settings import CENTRAL_URL

#XXX Make sure this is restartable at any point, in case the client
#    crashes/is shutdown/reloads HTML/etc.
#XXX Stale tabs sticking around keep polling w/ javascript, maybe APIKEY or something?

#These globals require either a threaded WSGI server, serial, or asyncio one.
privsub = None
def do_priv(cmd):
    global privsub
    if not privsub:
        #XXX Handle cancelled sudo here.
        import __main__
        privsub = osal.sudo(sys.executable, os.path.abspath(__main__.__file__), "--privsub")
        line = privsub.stdout.readline().strip() #XXX timeout?
        if line != "ok":
            raise Exception("privsub startup failed: '%s'" % line)

    privsub.stdin.write(cmd + '\n')
    privsub.stdin.flush()

    line = privsub.stdout.readline().strip()
    if line.startswith("ERROR "):
        raise Exception("privsub cmd %s failed: '%s'" % (cmd, line))
    return line

def finish_priv():
    global privsub
    if privsub:
        try:
            do_priv('exit')
            privsub.wait(timeout=5)
            privsub = None
        except:
            pass
atexit.register(finish_priv)

datacache = {}
def get_from_datadir(name):
    if not name in datacache:
        try:
            datadir = appdirs.user_data_dir("boundery")
            with open(os.path.join(datadir, name), 'r') as f:
                datacache[name] = f.read().strip()
        except:
            datacache.pop(name, None)
    return datacache.get(name, None)
def save_to_datadir(name, val):
    datadir = appdirs.user_data_dir("boundery")
    os.makedirs(datadir, exist_ok=True)
    with open(os.path.join(datadir, name), 'w') as f:
        f.write(val)
    datacache[name] = val

def get_subkey(keyname, salt = None):
    b64_pairing_key = get_from_datadir("pairingkey")
    if b64_pairing_key is None:
        pairing_key = random(32)
        save_to_datadir("pairingkey",
                            standard_b64encode(pairing_key).decode('ascii'))
    else:
        pairing_key = standard_b64decode(b64_pairing_key)

    if type(keyname) == str:
        keyname = keyname.encode()
    return hkdf_expand(hkdf_extract(salt, pairing_key), keyname, 32)

bootstrap_ipv6 = None
network_id = None

#########################

@get('/')
@get('/step1')
def step1():
    ssids = osal.get_ssids()
    ssids = [ ("%s (signal %s)" % (ssid[2], ssid[1]), ssid[2], ssid[0]) for ssid in ssids ]
    return template("step1", { "mountlist": step1_api1(), "ssids": ssids })

@get('/step1_api1')
def step1_api1():
    #XXX Emit a useful message if there are no mounts!
    return template("step1_api1", { "mounts": osal.get_mounts() })

step1_thread = None
@post('/step1')
def step1_post():
    mount = request.forms.get('mount')
    if mount not in osal.get_mounts():
        raise Exception("Bad mountpoint from client!")

    ssid = request.forms.get("ssid").strip()
    if ssid == "other":
        ssid = request.forms.get("other_ssid").strip()
    else:
        ssid = ssid[1:]

    global step1_thread
    step1_thread = Thread(target=step1_handler, name="step1_thread",
                              kwargs = { "ssid": ssid,
                                            "wifi_pw": request.forms.get("wifi_pw"),
                                             "mount": mount })
    step1_thread.cur = 0
    step1_thread.max = 103
    step1_thread.start()

    return template("step1_post")

def step1_handler(ssid, wifi_pw, mount):
    if "ZIPFILE" not in os.environ:
        #XXX More granular progress than just per-file.  Monkeypatch shutil.copyfileobj?
        r = requests.get(CENTRAL_URL + "/static/images/rpi3.zip", stream=True)
        bio = io.BytesIO()
        zip_length = r.headers.get('content-length')
        if zip_length is None:
            bio.write(r.content)
            step1_thread.cur = 50
        else:
            zip_length = int(zip_length)
            bytes_written = 0
            for chunk in r.iter_content(64*1024):
                bytes_written += len(chunk)
                bio.write(chunk)
                step1_thread.cur = (bytes_written / zip_length) * 50
    else:
        bio = open(os.environ["ZIPFILE"], 'rb')
        zip_length = os.path.getsize(os.environ["ZIPFILE"])
        step1_thread.cur = 50

    with zipfile.ZipFile(bio) as zf:
        zis = zf.infolist()
        num_bytes = reduce(add, [ zi.file_size for zi in zis ])
        bytes_written = 0
        for zi in zis:
            zf.extract(zi, path=mount)
            bytes_written += zi.file_size
            step1_thread.cur = 50 + (bytes_written / num_bytes) * 50
    bio.close()

    with open(os.path.join(mount, "pairingkey"), 'wb') as f:
        get_subkey("throwaway") #Make sure the key is loaded.
        f.write(standard_b64decode(get_from_datadir("pairingkey")))
    step1_thread.cur += 1

    if len(ssid) > 0:
        with open(os.path.join(mount, "wifi.txt"), 'w') as f:
            #XXX Verify that no-pw wifi networks work.
            f.write("%s\n%s\n" % (ssid, wifi_pw))
    else:
        try:
            os.remove(os.path.join(mount, "wifi.txt"))
        except FileNotFoundError:
            pass
    step1_thread.cur += 1

    try:
        os.remove(os.path.join(mount, "apikey"))
    except FileNotFoundError:
        pass
    step1_thread.cur += 1


@get('/step1_api2')
def step1_api2():
    global step1_thread
    if step1_thread.cur == step1_thread.max:
        step1_thread.join()
    return { 'cur': int(step1_thread.cur), 'max': step1_thread.max }

@get('/step2')
def step2():
    if ':' in request.urlparts.netloc:
        port = request.urlparts.netloc.split(':')[1]
    else:
        port = 80
    return template("step2", port=port, central_url=CENTRAL_URL)

@get('/step3')
def step3():
    #XXX What to do if there is no apikey in request?
    apikey = request.query.apikey
    username = request.query.username

    #XXX Handle errors writing.
    save_to_datadir("apikey", apikey)
    save_to_datadir("username", username)

    return template("step3")

@get('/step4')
def step4():
    do_priv("join ff05390539000000")
    return template("step4", central_url=CENTRAL_URL)

@post('/step4_api1')
def step4_api1():
    pairing_id = standard_b64encode(get_subkey("pairing_id"))
    r = requests.post(CENTRAL_URL + "/api/v1/get_server_bootstrap/",
                        data = { "APIKEY": get_from_datadir("apikey"),
                                   "PAIRING_ID": pairing_id, })
    if r.status_code == 200:
        global bootstrap_ipv6
        bootstrap_ipv6 = r.json()["bootstrap_ipv6"]
        return "ok"
    else:
        abort(404, "Not found")

@post('/step4_api2')
def step4_api2():
    hkdf_salt = random(32)
    nodeid = do_priv("get_nodeid")
    to_server_key = get_subkey("to_server", hkdf_salt)
    ciphertext = SecretBox(to_server_key).encrypt(nodeid.encode())

    try:
        with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((bootstrap_ipv6, 1337))

            assert(len(hkdf_salt) < 256)
            s.sendall(len(hkdf_salt).to_bytes(1, byteorder='big') + hkdf_salt)
            assert(len(ciphertext) < 256)
            s.sendall(len(ciphertext).to_bytes(1, byteorder='big') + ciphertext)

            num_bytes = int.from_bytes(s.recv(1), byteorder='big')
            resp=b''
            while len(resp) < num_bytes:
                resp += s.recv(num_bytes - len(resp))
    except (OSError, socket.timeout):
        abort(404, "Not found")

    from_server_key = get_subkey("from_server", hkdf_salt)
    global network_id
    network_id = SecretBox(from_server_key).decrypt(resp).decode()

    do_priv("join %s" % network_id)

    return "ok"

@post('/step4_api3')
def step4_api3():
    status = do_priv("joinstatus %s" % network_id)
    if status == "OK":
        do_priv("leave ff05390539000000")
        return "ok"
    else:
        abort(404, "Not found")

#########################

def zt_do(authtoken, method, path, data = None):
    headers = { 'Connection': 'close',
                'Content-Type': 'application/json',
                'X-ZT1-Auth': authtoken }

    url = "http://localhost:9993/%s" % path

    if data is not None:
        r = method(url, headers = headers, data = json.dumps(data))
    else:
        r = method(url, headers = headers)

    if r.status_code == 200 and len(r.text) != 0:
        return r.json()
    else:
        return None

def zt_get(authtoken, path):
    return zt_do(authtoken, requests.get, path)
def zt_post(authtoken, path, data):
    return zt_do(authtoken, requests.post, path, data)
def zt_delete(authtoken, path):
    return zt_do(authtoken, requests.delete, path)

def privsub_run():
    try:
        with open(osal.get_zerotier_token_path(), 'r') as f:
            authtoken = f.read().strip()
    except:
        authtoken = None
    if authtoken is None or authtoken == '':
        print("ERROR can't read authtoken")
        sys.exit(10)
    print("ok")
    sys.stdout.flush()

    for line in sys.stdin:
        try:
            line = line.strip()
            if line == "get_nodeid":
                json = zt_get(authtoken, "status")
                print(json.get("address"))
            elif line.startswith("join "):
                netid = line.split(' ')[1]
                zt_post(authtoken, "network/%s" % netid, {})
                print("ok") #XXX Error handling
            elif line.startswith("joinstatus "):
                netid = line.split(' ')[1]
                status = zt_get(authtoken, "network/%s" % netid).get("status", "")
                print(status)
            elif line.startswith("leave "):
                netid = line.split(' ')[1]
                zt_delete(authtoken, "network/%s" % netid)
                print("ok") #XXX Error handling
            elif line == "exit":
                sys.exit()
        except Exception as e:
            print("ERROR exception %s" % repr(e))

        sys.stdout.flush()
        sys.stderr.flush()
