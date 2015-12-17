#!/usr/bin/python
from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from webapp import app
import threading
import control

def doStuff():
    controller=threading.Thread(target=control.start)
    controller.daemon=True
    controller.start()
    IOLoop.instance().start()

if __name__ == "__main__":
    doStuff()
