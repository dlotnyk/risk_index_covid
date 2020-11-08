import threading
import time
from wsgiref.simple_server import make_server
from flask import Flask, render_template, jsonify, request
from logger import log_settings
from api_call import take_date

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
        # return render_template("layout.html")
        return render_template("mainPage.html")

    @flask_app.route("/simple_chart")
    def chart():
        app_log.debug("Route `Simple_chart` is called")
        country_code = request.args.get("state")
        s_date = request.args.get("start_date")
        e_date = request.args.get("end_date")
        contact_strategy = request.args.get("contact_strategy")
        dates, si, country, ri, cases, log_cases = take_date(country_code=country_code,
                                                             start_date=s_date,
                                                             end_date=e_date,
                                                             contact_strategy=contact_strategy)
        legend = "Stringency index"
        legend2 = "Risk index"
        legend3 = "Cases"
        legend4 = "Deaths"
        app_log.info(f"country `{country_code}`, from `{s_date}` to "
                     f"`{e_date}` strat {contact_strategy}")
        return jsonify(dates=dates, si=si, country=country, cases=cases,
                       log_cases=log_cases, ri=ri)
        # return render_template('chart.html', country=country, labels=dates,
        #                        values=si,  legend=legend,
        #                        values2=ri, legend2=legend2,
        #                        values3=cases, legend3=legend3,
        #                        values4=death, legend4=legend4)
    return flask_app


if __name__ == "__main__":
    app_log.info("flask app starts")
    http_thread = WsgiRefServer(get_app())
    http_thread.start()
    time.sleep(120)
    http_thread.stop()
    # get_app().debug = True
    # get_app().run()
    app_log.info("flask app stops")
