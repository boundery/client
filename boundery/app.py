import sys, time
import requests
import webbrowser
from bottle import route, run
from threading import Thread

#XXX Try random ports until one works.

#XXX Need some way to pull in other files with @route decorators.

POLL_INTERVAL = 0.5

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
    webbrowser.open("http://localhost:8080/")

poller = Thread(target=poll_ready, name="poll_ready", daemon=True)
poller.start()

if "--debug" in sys.argv:
    run(host="localhost", port=8080, debug=True)
else:
    run(host='0.0.0.0', port=8080, debug=False, server='waitress')
