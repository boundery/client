import os, subprocess, objc, appdirs

#https://stackoverflow.com/questions/49171769/how-where-to-best-retrieve-sudo-password-via-a-native-gui-on-a-macos-python-ba

def get_mounts():
    ret = []
    p = subprocess.run(["mount"], stdout=subprocess.PIPE, universal_newlines=True)
    for line in p.stdout.split('\n'):
        dev, on, mnt, *options = line.split()
        assert(on == "on")
        if mnt == '/':
            continue
        if not options[0].startswith("(msdos"):
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

    scriptname = os.path.join(appdirs.user_data_dir("boundery"), "script.sh")
    with open(scriptname, 'w') as script:
        script.write('#!/bin/sh')
        script.write("exec %s %s" % (sys.executable, ' '.join([ '"'+a+'"' for a in fullargs ])))
    os.chmod(scriptname, 0o555)

    osascript = r"""do shell script "%s" with prompt "Create private networks" with administrator privileges""" % scriptname

    topriv = os.path.join(appdirs.user_data_dir("boundery"), "topriv")
    frompriv = os.path.join(appdirs.user_data_dir("boundery"), "frompriv")
    os.mkfifo(topriv)
    os.mkfifo(frompriv)

    p = subprocess.Popen(["osascript", "-e", osascript])
    p.stdin = open(topriv, 'w')
    p.stdout = open(frompriv, 'r')
    p.stderr = p.stdout
    return NPWrapper(topriv, frompriv)

def get_zerotier_token_path():
    return "/Library/Application Support/ZeroTier/One/authtoken.secret"

def get_ssids():
    ssids = []
    objc.loadBundle('CoreWLAN',
                    bundle_path='/System/Library/Frameworks/CoreWLAN.framework',
                    module_globals=globals())
    iface = CWInterface.interface()
    aps, err = iface.scanForNetworksWithName_includeHidden_error_(None, True, None)
    for ap in aps:
        if ap.ssid() is None:
            continue
        if ap.ibss():
            continue
        #XXX Figure out which SSID client is currently connected to.
        ssids.append((False, min(max(2 * (ap.rssiValue() + 100), 0), 100), ap.ssid()))
    return ssids
