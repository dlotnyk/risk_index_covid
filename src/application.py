import threading
import time
from wsgiref.simple_server import make_server
from flask import Flask, render_template, url_for
from logger import log_settings
from main import take_date

app_log = log_settings()


class WsgiRefServer(threading.Thread):

    def __init__(self, wsgi_app, host='127.0.0.1', port=5000):
        super().__init__()
        self._server = make_server(host, port, wsgi_app)

    def run(self):
        app_log.debug("WSGI server starts")
        self._server.serve_forever(poll_interval=0.5)

    def stop(self):
        app_log.debug("WSGI server stops")
        self._server.shutdown()
        self.join()


def get_app():
    flask_app = Flask(__name__, template_folder="templates", static_folder="static")

    @flask_app.route("/")
    @flask_app.route("/home")
    def home():
        app_log.debug("Route `home` is called")
        return render_template("home.html")

    @flask_app.route("/simple_chart")
    def chart():
        app_log.debug("Route `Simple_chart` is called")
        dates, si, country, ri, cases, death = take_date()
        legend = "Stringency index"
        legend2 = "Risk index"
        legend3 = "Cases"
        legend4 = "Deaths"
        return render_template('chart.html', country=country, labels=dates,
                               values=si,  legend=legend,
                               values2=ri, legend2=legend2,
                               values3=cases, legend3=legend3,
                               values4=death, legend4=legend4)

    @flask_app.route("/line_chart")
    def line_chart():
        legend = 'Temperatures'
        temperatures = [73.7, 73.4, 73.8, 72.8, 68.7, 65.2,
                        61.8, 58.7, 58.2, 58.3, 60.5, 65.7,
                        70.2, 71.4, 71.2, 70.9, 71.3, 71.1]
        times = ['12:00PM', '12:10PM', '12:20PM', '12:30PM', '12:40PM', '12:50PM',
                 '1:00PM', '1:10PM', '1:20PM', '1:30PM', '1:40PM', '1:50PM',
                 '2:00PM', '2:10PM', '2:20PM', '2:30PM', '2:40PM', '2:50PM']
        return render_template('line_chart.html', values=temperatures, labels=times, legend=legend)

    @flask_app.route("/si_chart")
    def si_chart():
        dates, si, country = take_date()
        legend = "Stringency index"
        return render_template("line_chart.html", values=si, labels=dates, legend=legend, country=country)

    return flask_app


if __name__ == "__main__":
    app_log.info("flask app starts")
    http_thread = WsgiRefServer(get_app())
    http_thread.start()
    time.sleep(60)
    http_thread.stop()
    # get_app().debug = True
    # get_app().run()
    app_log.info("flask app stops")
