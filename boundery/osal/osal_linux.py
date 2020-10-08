import sys, os, subprocess

def get_mounts():
    #XXX Check for /sys/sda/sdd/removable?
    ret = []
    with open("/proc/mounts", 'r') as f:
        for line in f:
            if not line.startswith("/dev/"):
                continue
            (dev, mnt, fs, opts, dummy, dummy) = line.split(maxsplit=6)
            if fs != 'vfat':
                continue
            mnt = mnt.replace('\\040', ' ').replace('\\011', '\t')
            mnt = mnt.replace('\\134', '\\').replace('\\012', '\n')
            if mnt == "/" or mnt.startswith("/boot"):
                continue
            if not os.access(mnt, os.W_OK):
                continue
            #XXX Maybe include the LABEL in the first, human readable element?
            ret.append((mnt.split('/')[-1], mnt))
    return ret

#XXX Some fallback if pkexec isn't available?  sudo in a terminal?
def sudo(cmd, *args):
    fullargs = [ '/bin/sh', '-c', "PYTHONPATH='%s' '%s' %s" %
                 (':'.join(sys.path), cmd, ' '.join(["'%s'" % a for a in args ]))]
    return subprocess.Popen(["pkexec", *fullargs],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            stdin=subprocess.PIPE,
                            bufsize=1, universal_newlines=True)

def get_zerotier_token_path():
    return "/var/lib/zerotier-one/authtoken.secret"

#XXX Support wicd.
#XXX Fallback to talking to the card directly.
def get_ssids():
    p = subprocess.run(["nmcli", "-t", "-f", "mode,active,signal,ssid", "dev", "wifi"],
                           stdout=subprocess.PIPE, universal_newlines=True)
    ssids = []
    for ssid in p.stdout.splitlines():
        ssid = ssid.split(':', 3)
        if ssid[0] != "Infra":
            continue
        ssids.append(ssid[1:])
    ssids = [ (i[0] == 'yes', int(i[1]), i[2]) for i in ssids ]
    return ssids
