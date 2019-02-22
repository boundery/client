from bottle import route

@route('/')
def root():
    return "Hello world?"
