import sys, os, subprocess, re, appdirs
from ctypes import cdll, util
from rubicon.objc import ObjCClass

#https://stackoverflow.com/questions/49171769/how-where-to-best-retrieve-sudo-password-via-a-native-gui-on-a-macos-python-ba

mount_re = re.compile(r'^/dev/[a-zA-Z0-9]+ on (/Volumes/[^/]+) [(](.+)[)]$')
def get_mounts():
    ret = []
    p = subprocess.run(["mount"], stdout=subprocess.PIPE, universal_newlines=True)
    for line in p.stdout.split('\n'):
        match = mount_re.match(line)
        if not match:
            continue
        mnt = match.groups()[0]
        options = match.groups()[1].split(', ')
        if "msdos" not in options:
            continue
        if not os.access(mnt, os.W_OK):
            continue
        ret.append(mnt)
    return ret

#osascript's elevate command does weird stuff to stdin/stdout, so we use a pair of fifos.
def sudo(cmd, *args):
    fullargs = [ os.path.join(os.path.dirname(__file__),
                                  'osal_elevate.py'), cmd ]
    fullargs.extend(args)
    fullargs.append('--')
    fullargs.extend(sys.path)

    boundery_dir = appdirs.user_data_dir("boundery")
    os.makedirs(boundery_dir, exist_ok=True)
    scriptname = os.path.join(boundery_dir, "script.sh")
    with open(scriptname, 'w') as script:
        script.write('#!/bin/sh\n')
        script.write('exec "%s" %s\n' % (sys.executable, ' '.join([ '"'+a+'"' for a in fullargs ])))
    os.chmod(scriptname, 0o755)

    #XXX Hack: we replace ' ' with '?' because I couldn't get osascript quoting right.
    osascript = r"""do shell script "%s" with prompt "Create private networks" with administrator privileges""" % scriptname.replace(' ', '?')

    topriv = os.path.join(boundery_dir, "topriv")
    frompriv = os.path.join(boundery_dir, "frompriv")
    try:
        os.remove(topriv)
    except FileNotFoundError:
        pass
    try:
        os.remove(frompriv)
    except FileNotFoundError:
        pass
    os.mkfifo(topriv, mode=0o700)
    os.mkfifo(frompriv, mode=0o700)

    p = subprocess.Popen(["osascript", "-e", osascript])
    p.stdin = open(topriv, 'w')
    p.stdout = open(frompriv, 'r')
    p.stderr = p.stdout
    return p

def get_zerotier_token_path():
    return "/Library/Application Support/ZeroTier/One/authtoken.secret"

def get_ssids():
    ssids = []
    cdll.LoadLibrary(util.find_library('CoreWLAN'))
    CWInterface = ObjCClass('CWInterface')
    interface = CWInterface.interface()
    if interface:
        aps = interface.scanForNetworksWithName_includeHidden_error_(None, True, None)
        for ap in aps.allObjects():
            if str(ap.ssid) is None:
                continue
            if int(ap.ibss):
                continue
            #XXX Figure out which SSID client is currently connected to.
            ssids.append((False, min(max(2 * (int(ap.rssiValue) + 100), 0), 100), str(ap.ssid)))
    return ssids

def self_test():
    import logging
    try:
        print("Testing get_mounts")
        mounts = get_mounts()
        if '/Volumes/BOUNDERYTST' not in mounts:
            logging.error("get_mounts failed: '%s'" % mounts)
            return 10

        print("Testing ZT info")
        zt = sudo('zerotier-cli', 'info')
        zt_out = zt.stdout.read()
        if not zt_out.startswith('200 info '):
            logging.error("sudo failed: '%s'" % zt_out)
            return 20

        print("Testing get_ssids")
        ssids = get_ssids()
        print("Testing complete")
    except:
        logging.error("foo", exc_info=True)
        return 99
