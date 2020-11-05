import threading
import time
from wsgiref.simple_server import make_server
from flask import Flask, render_template, url_for


class WsgiRefServer(threading.Thread):

    def __init__(self, wsgi_app, host='127.0.0.1', port=5000):
        super().__init__()
        self._server = make_server(host, port, wsgi_app)

    def run(self):
        self._server.serve_forever(poll_interval=0.5)

    def stop(self):
        self._server.shutdown()
        self.join()


def get_app():
    flask_app = Flask(__name__, template_folder="templates", static_folder="static")

    @flask_app.route("/")
    @flask_app.route("/home")
    def home():
        return render_template("home.html")

    return flask_app


if __name__ == "__main__":
    http_thread = WsgiRefServer(get_app())
    http_thread.start()
    time.sleep(60)
    http_thread.stop()