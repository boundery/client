import sys, time, os

#Something bottle does in run() blows up if sys.std* are None when bottle is imported.
if '--privsub' not in sys.argv:
    if sys.executable.upper().endswith("\\PYTHONW.EXE"):
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
        sys.stdin = open(os.devnull, 'r')

import requests
import webbrowser
import appdirs
from bottle import route, run, static_file, TEMPLATE_PATH
from collections import namedtuple
from threading import Thread
from boundery import settings

#XXX Add some APIKEY between browser and this server.
#XXX Add JS to make it quit the deamon when all browser tabs/windows are closed.  Also, timeout.

POLL_INTERVAL = 0.5

TEMPLATE_PATH.clear()
TEMPLATE_PATH.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"))

if "--local" in sys.argv:
    settings.CENTRAL_URL = "http://localhost:8000"
DEBUG = "--debug" in sys.argv

#Pull in the various routes.
from boundery import enroll

@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename,
                       root=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         'static'))

@route('/server_ok')
def server_ok():
    return "ok"

def poll_ready():
    while True:
        try:
            r = requests.get("http://localhost:%s/server_ok" % settings.PORT)
            r.close()
            if r.status_code == 200:
                break
        except:
            pass
        time.sleep(POLL_INTERVAL)
    webbrowser.open("http://localhost:%s/" % settings.PORT)

def main():
    if os.environ.get('BOUNDERY_APP_TEST', '') == '1':
        from boundery import osal
        sys.exit(osal.self_test())
    elif "--privsub" in sys.argv:
        enroll.privsub_run()
    else:
        if sys.executable.upper().endswith("\\PYTHONW.EXE"):
            sys.stdout = open(os.path.join(appdirs.user_data_dir("boundery"), "out.log"), 'w')
            sys.stderr = open(os.path.join(appdirs.user_data_dir("boundery"), "err.log"), 'w')

        poller = Thread(target=poll_ready, name="poll_ready", daemon=True)
        poller.start()

        if DEBUG:
            run(host="localhost", port=settings.PORT, debug=True)
        else:
            run(host="localhost", port=settings.PORT, debug=False, server='waitress')

    #briefcase expects main to return an object w/ a function on win32.
    return namedtuple('Dummy', 'main_loop')(main_loop = lambda: None)
