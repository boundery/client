import sys, time, os
import requests
import webbrowser
from bottle import route, run, static_file, TEMPLATE_PATH
from threading import Thread
from boundery import settings

#XXX Add some APIKEY between browser and this server.
#XXX Add JS to make it quit the deamon when all browser tabs/windows are closed.

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
    if "--privsub" in sys.argv:
        enroll.privsub_run()
    else:
        poller = Thread(target=poll_ready, name="poll_ready", daemon=True)
        poller.start()
        if DEBUG:
            run(host="localhost", port=settings.PORT, debug=True)
        else:
            run(host="localhost", port=settings.PORT, debug=False, server='waitress')
