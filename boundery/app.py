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
from boundery import settings, ui

#XXX Add some APIKEY between browser and this server.

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

def serve():
    if DEBUG:
        run(host="localhost", port=settings.PORT, debug=True)
    else:
        run(host="localhost", port=settings.PORT, debug=False, server='waitress')

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

        server = Thread(target=serve, name="api_server", daemon=True)
        server.start()

        poll_ready()

        if '--no-gui' in sys.argv or 'DISPLAY' not in os.environ:
            webbrowser.open("http://localhost:%s/" % settings.PORT)
            server.join()
        else:
            return ui.App(initial_url="http://localhost:%s/" % settings.PORT)

    #briefcase expects main to return an object w/ a function on win32.
    return namedtuple('Dummy', 'main_loop')(main_loop = lambda: None)
