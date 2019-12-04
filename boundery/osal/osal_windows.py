import sys, os, subprocess

#briefcase's start.py adds app_packages to sys.path, which skips pywin32's .pth file. sitedirs don't.
import site
site.addsitedir(next(filter(lambda i: i.endswith('app_packages'), sys.path), ''))

from ctypes import windll, create_unicode_buffer, sizeof, c_wchar_p

from . import win32wifi
import win32pipe, win32file, msvcrt

def get_mounts():
    DRIVE_REMOVABLE = 2
    DRIVE_CDROM = 5
    buf = create_unicode_buffer(1024)
    count = windll.kernel32.GetLogicalDriveStringsW(sizeof(buf)-1, buf)
    drives = buf[:count-1].split('\x00')

    ret = []
    for drive in drives:
        if os.environ.get("BOUNDERY_ENUM_FIXED", None):
            if drive[0] == 'C' or windll.kernel32.GetDriveTypeW(drive) == DRIVE_CDROM:
                continue
        else:
            if windll.kernel32.GetDriveTypeW(drive) != DRIVE_REMOVABLE:
                continue
        volume_name = create_unicode_buffer(1024)
        fs_type = create_unicode_buffer(1024)
        windll. kernel32.GetVolumeInformationW(c_wchar_p(drive),
                                               volume_name, sizeof(volume_name)-1,
                                               None, None, None,
                                               fs_type, sizeof(fs_type)-1)
        if not fs_type.value.startswith('FAT'):
            continue
        ret.append((volume_name.value, drive[:2]))

    return ret

class NPWrapper:
    def __init__(self, pipe):
        win32pipe.ConnectNamedPipe(pipe, None)
        self._pipe = pipe
        self.stdin = open(msvcrt.open_osfhandle(pipe, os.O_WRONLY), 'w')
        self.stdout = open(msvcrt.open_osfhandle(pipe, os.O_RDONLY), 'r')
        self.stderr = open(msvcrt.open_osfhandle(pipe, os.O_RDONLY), 'r')

    def wait(self, timeout = -1):
        #XXX Need to actually wait here?
        win32file.CloseHandle(self._pipe)

#Windows UAC (runas) doesn't hook up stdin/out. So we use a named pipe and a helper process.
def sudo(cmd, *args):
    pipe = win32pipe.CreateNamedPipe(r'\\.\pipe\BounderySudo',
        win32pipe.PIPE_ACCESS_DUPLEX,
        win32pipe.PIPE_TYPE_BYTE | win32pipe.PIPE_READMODE_BYTE |
        win32pipe.PIPE_WAIT, 1, 65536, 65536, 0, None)

    fullargs = [ os.path.join(os.path.dirname(__file__),
                                  'osal_elevate.py'), cmd ]
    fullargs.extend(args)
    fullargs.append('--')
    fullargs.extend(sys.path)
    python = sys.executable
    if python.upper().endswith('\\PYTHON.EXE'):
        python = python[:-len('python.exe')] + 'pythonw.exe'
    if fullargs[1].upper().endswith('\\PYTHON.EXE'):
        fullargs[1] = fullargs[1][:-len('python.exe')] + 'pythonw.exe'
    windll.shell32.ShellExecuteW(None, "runas",
                                 python, subprocess.list2cmdline(fullargs), None, 1)
    return NPWrapper(pipe)

def get_zerotier_token_path():
    return "C:\\ProgramData\\ZeroTier\\One\\authtoken.secret"

def get_ssids():
    #XXX Figure out which SSID client is currently connected to.
    #XXX Filter out non AP mode aps here.
    return [ (False, min(max(2 * (x[1] + 100), 0), 100), x[0]) for x in win32wifi.get_BSSI().values() ]
