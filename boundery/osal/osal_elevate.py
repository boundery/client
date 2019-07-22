import sys

sys.path = sys.argv[sys.argv.index('--')+1:]
cmdargs = sys.argv[1:sys.argv.index('--')]

import time, os, subprocess
import appdirs

#briefcase's start.py adds app_packages to sys.path, which skips pywin32's .pth file. sitedirs don't.
import site
site.addsitedir(next(filter(lambda i: i.endswith('app_packages'), sys.path), ''))

out = open(os.path.join(appdirs.user_data_dir("boundery"), "elevate.log"), 'w')

if os.name == "nt":
    import pywintypes, win32file, msvcrt
    def pipe_client():
        quit = False
        while not quit:
            try:
                print("Connecting to named pipe", file=out, flush=True)
                pipe = win32file.CreateFile(r'\\.\pipe\BounderySudo',
                                                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                                                0, None, win32file.OPEN_EXISTING, 0, None)

                print("Starting: '%s' -- '%s'" % (cmdargs, sys.path), file=out, flush=True)
                stdin = open(msvcrt.open_osfhandle(pipe, os.O_RDONLY), 'r')
                stdout = open(msvcrt.open_osfhandle(pipe, os.O_WRONLY), 'w')
                subprocess.Popen(cmdargs, stdin=stdin, stdout=stdout, stderr=subprocess.STDOUT)

                quit=True
            except pywintypes.error as e:
                if e.args[0] == 2:
                    print("no pipe, trying again in a sec", file=out, flush=True)
                    time.sleep(1)
                elif e.args[0] == 109:
                    print("broken pipe, bye bye", file=out, flush=True)
                    quit = True
                else:
                    print("other? %s" % e, file=out, flush=True)
                    quit = True
        win32file.CloseHandle(pipe)
        print("Done", file=out, flush=True)
elif os.name == "posix":
    def pipe_client():
        print("Connecting to fifos", file=out, flush=True)
        topriv = open(os.path.join(appdirs.user_data_dir("boundery"), "topriv"), 'r')
        frompriv = open(os.path.join(appdirs.user_data_dir("boundery"), "frompriv"), 'w')

        print("Starting: '%s' -- '%s'" % (cmdargs, sys.path), file=out, flush=True)
        subprocess.Popen(cmdargs, stdin=topriv, stdout=frompriv, stderr=subprocess.STDOUT)
        print("Done", file=out, flush=True)
else:
    assert(False)

if __name__ == '__main__':
    try:
        pipe_client()
    except BaseException as e:
        print("Exception: %s" % e, file=out, flush=True)
    out.close()
