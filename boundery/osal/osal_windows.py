import sys, os, subprocess, ctypes

#briefcase's start.py adds app_packages to sys.path, which skips pywin32's .pth file. sitedirs don't.
import site
site.addsitedir(next(filter(lambda i: i.endswith('app_packages'), sys.path), ''))

from . import win32wifi
import pywintypes, win32pipe, win32file, msvcrt
from win32api import GetLogicalDriveStrings
from win32file import GetDriveType

#XXX Would be nice to get human-readable description as well...
def get_mounts():
    drives = GetLogicalDriveStrings()
    drives = [i for i in drives.split("\x00") if i]
    return [i[:2] for i in drives if GetDriveType(i) == win32file.DRIVE_REMOVABLE]

def _pipe_handle(pipe):
    try:
        win32pipe.ConnectNamedPipe(pipe, None)
        while True:
            result, resp = win32file.ReadFile(pipe, 64*1024)
            print("message: %s" % resp)

        print("Client connected")
    except pywintypes.error as e:
        if e.args[0] == 109:
            print("broken pipe, bye bye")
        else:
            print("other? %s" % e)
    finally:
        win32file.CloseHandle(pipe)

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
                                  'osal_windows_elevate.py'), cmd ]
    fullargs.extend(args)
    fullargs.append('--')
    fullargs.extend(sys.path)
    python = sys.executable
    if python.upper().endswith('\\PYTHON.EXE'):
        python = python[:-len('python.exe')] + 'pythonw.exe'
    if fullargs[1].upper().endswith('\\PYTHON.EXE'):
        fullargs[1] = fullargs[1][:-len('python.exe')] + 'pythonw.exe'
    ctypes.windll.shell32.ShellExecuteW(None, "runas",
                                            python, subprocess.list2cmdline(fullargs), None, 1)

    return NPWrapper(pipe)

def get_zerotier_token_path():
    return "C:\\ProgramData\\ZeroTier\\One\\authtoken.secret"

def get_ssids():
    #XXX Figure out which SSID client is currently connected to.
    return [ (False, min(max(2 * (x[1] + 100), 0), 100), x[0]) for x in win32wifi.get_BSSI().values() ]
