import sys, time
import requests
import webbrowser
from bottle import route, run
from threading import Thread

#XXX Try random ports until one works.  Bottle doesn't make this easy, since
#    we don't know if a port can be bound until we're deep in run, and thus
#    can't run our own code...

#XXX Need some way to pull in other files with @route decorators.

POLL_INTERVAL = 0.5
PORT=1337

@route('/server_ok')
def root():
    return "ok"

def poll_ready():
    while True:
        try:
            r = requests.get("http://localhost:8080/server_ok")
            r.close()
            if r.status_code == 200:
                break
        except:
            pass
        time.sleep(POLL_INTERVAL)
    webbrowser.open("http://localhost:%s/" % PORT)

poller = Thread(target=poll_ready, name="poll_ready", daemon=True)
poller.start()

if "--debug" in sys.argv:
    run(host="localhost", port=PORT, debug=True)
else:
    run(host='0.0.0.0', port=PORT, debug=False, server='waitress')
