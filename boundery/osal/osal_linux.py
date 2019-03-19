import os, subprocess

def get_mounts():
    ret = []
    with open("/proc/mounts", 'r') as f:
        for line in f:
            if not line.startswith("/dev/"):
                continue
            (dev, mnt, fs, opts, dummy, dummy) = line.split(maxsplit=6)
            if mnt == "/" or mnt.startswith("/boot") or mnt.startswith("/run/user"):
                continue
            if not os.access(mnt, os.W_OK):
                continue
            ret.append(mnt)
    return ret

#XXX Some fallback if pkexec isn't available?  sudo in a terminal?
def sudo(cmd, *args):
    return subprocess.Popen(["pkexec", cmd, *args],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                stdin=subprocess.PIPE,
                                bufsize=1, universal_newlines=True)

def get_data_dir(name):
    xdg = os.environ.get("XDG_DATA_HOME", None)
    if xdg and os.path.isdir(xdg):
        datadir = os.path.join(d, name)
    elif os.path.isdir(os.path.expanduser("~/.local/share")):
        datadir = os.path.join(os.path.expanduser("~/.local/share"), name)
    else:
        datadir = os.path.join(os.path.expanduser("~/.%s" % name))
    os.makedirs(datadir, exist_ok=True)
    return datadir

def get_zerotier_token_path():
    return "/var/lib/zerotier-one/authtoken.secret"
