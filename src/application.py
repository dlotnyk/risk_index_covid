from typing import Dict
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, jsonify, request
import requests
from datetime import timedelta, date
import json
import math
from logger import log_settings

stringency = "stringency"
cases_str = "confirmed"
death_str = "deaths"
dateformat = "%Y-%m-%d"
payload = dict()
headers = dict()

def log_settings():
    #  Logger definitions
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - line: %(lineno)d - %(message)s')
    logFile = "risk_index.log"
    my_handler = RotatingFileHandler(logFile, mode="a", maxBytes=20 * 1024 * 1024, backupCount=2, encoding=None,
                                     delay=False)
    my_handler.setFormatter(log_formatter)
    my_handler.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.DEBUG)
    app_log = logging.getLogger("RiskIndex")
    app_log.setLevel(logging.DEBUG)
    if len(app_log.handlers) < 2:
        app_log.addHandler(my_handler)
        app_log.addHandler(console_handler)
    return app_log

app_log = log_settings()

class MathModel:
    s_dict_begin = "begin"
    s_dict_end = "end"
    s_dict_result = "result"
    s_param_0 = "p0"
    s_param_1 = "p1"
    s_param_2 = "p2"
    days_params = {"0": {s_param_0: 68.6781539999999,
                         s_param_1: - 0.87130515892857,
                         s_param_2: 0.00205254330357142},
                   "1": {s_param_0: 82.9741629999999,
                         s_param_1: -0.745074860714284,
                         s_param_2: 0.0015394169642857},
                   "2": {s_param_0: 93.4626439999999,
                         s_param_1: -0.630388267857141,
                         s_param_2: 0.00134698660714284},
                   "3": {s_param_0: 97.70111,
                         s_param_1: -0.414869517857144,
                         s_param_2: 4.48986607142863E-4},
                   "4": {s_param_0: 100.79021,
                         s_param_1: -0.297618125,
                         s_param_2: 3.84843750000002E-4},
                   "5": {s_param_0: 101.364984,
                         s_param_1: -0.188835857142858,
                         s_param_2: 2.56582142857146E-4},
                   "6": {s_param_0: 101.436805,
                         s_param_1: -0.111094839285714,
                         s_param_2: 1.92433035714285E-4},
                   "7": {s_param_0: 99.856335,
                         s_param_1: 0.00307787500000054,
                         s_param_2: -3.84843750000007E-4}
                   }

    def __init__(self, stringency_index: float,
                 contact_strategy=70.0,
                 contact_strategy_high=80.0,
                 contact_strategy_low=60.0):
        """
        Init metod for Math calculations
        :param stringency_index: main parameter stringency index
        :param contact_strategy: default is 70
        :param contact_strategy_high: high error bar for estimation
        :param contact_strategy_low: low error bar for estimation
        """
        self.stringency_index = stringency_index
        self.contact_strategy = contact_strategy
        self.contact_strategy_high = contact_strategy_high
        self.contact_strategy_low = contact_strategy_low
        self._fit_dict: Dict = dict()
        self.init_fit_dict()

    @property
    def fit_dict(self):
        """
        Returns fit dictionary contains fitting parameters of testing delay at previuos day or `begin`,
        next day or `end` and the resulting `result`
        :return:
        """
        return self._fit_dict

    def init_fit_dict(self):
        """
        Initiates fit dictionary based on testing delay and days_param dictionary
        :return: fit_dict
        """
        day1 = str(int(self.testing_delay))
        day2 = str(int(self.testing_delay)+1)
        self._fit_dict = {self.s_dict_begin: self.days_params.get(day1, None),
                          self.s_dict_end: self.days_params.get(day2, None),
                          self.s_dict_result: {}}

    @property
    def testing_delay(self) -> float:
        """
        Returns resting delay based on stringency index as
        TD = 7 - 0.07 * SI
        Should be 0 < TD < 7
        :return: testing_delay
        """
        return 7 - 0.07 * self.stringency_index

    @staticmethod
    def fit_slope(begin_p: float, end_p: float) -> float:
        """
        Slope of the parameter fit. Such simple because days difference = 1
        slope = (p_e - p_b)(days_difference)
        :param begin_p: parameter for day before
        :param end_p: paramter for day after
        :return: slope
        """
        return end_p - begin_p

    @staticmethod
    def fit_intercept(begin_p: float) -> float:
        """
        returns intercept for parameter fit
        :param begin_p:
        :return: intercept
        """
        return begin_p

    def fit_parameters(self) -> None:
        """
        Calculates parameters for resulting quadratic fit.
        Updates fit_dict under key `result`
        """
        if self.fit_dict and self.fit_dict.get(self.s_dict_begin, None) is not None \
                and self.fit_dict.get(self.s_dict_end, None) is not None:
            for key1, key2 in zip(list(self.fit_dict.get(self.s_dict_begin).keys()),
                                  list(self.fit_dict.get(self.s_dict_end))):
                slope = self.fit_slope(self.fit_dict["begin"][key1], self.fit_dict["end"][key2])
                intercept = self.fit_intercept(self.fit_dict["begin"][key1])
                x = self.testing_delay - int(self.testing_delay)
                res = slope * x + intercept
                self._fit_dict["result"].update({key1: res})
            app_log.debug("Fit parameters for RI are calculated")
        else:
            app_log.error("Main dictionary does not exists or not full")

    def get_risk_index(self, cont_strat: float) -> float:
        """
        Returns the risk index based on `result` quadratic fit
        :param cont_strat:
        :return: RI
        """
        if self.fit_dict.get(self.s_dict_result):
            x0 = self.fit_dict[self.s_dict_result][self.s_param_0]
            x1 = self.fit_dict[self.s_dict_result][self.s_param_1] * cont_strat
            x2 = self.fit_dict[self.s_dict_result][self.s_param_2] * cont_strat * cont_strat
            return x0 + x1 + x2
        else:
            app_log.error("Data are not fitted yet")

    @property
    def get_main_data(self):
        """
        :return: tuple of RI for Contact Strategies
        """
        return self.get_risk_index(self.contact_strategy), self.get_risk_index(self.contact_strategy_low), self.get_risk_index(self.contact_strategy_high)

    @property
    def main_math(self):
        """
        main part. Executes all parts
        :return: tuple of RI for Contact Strategies user defined or default 60-low, 70-default, 80-high
        """
        self.fit_parameters()
        app_log.debug(f"RI are: {self.get_main_data}")
        return self.get_main_data

def daterange(start_date, end_date):
    for item in range(int((end_date - start_date).days)):
        yield start_date + timedelta(item)


def take_date(start_date, end_date, country_code, contact_strategy):
    dd1 = date.fromisoformat(start_date)
    dd2 = date.fromisoformat(end_date)
    url = f"https://covidtrackerapi.bsg.ox.ac.uk/api/v2/stringency/date-range/{start_date}/{end_date}"
    response = requests.request("GET", url, headers=headers, data=payload)
    resp = json.loads(response.text)
    dates = list()
    ri_list = list()
    ri_high = list()
    ri_low = list()
    d_dates = list()
    si_list = list()
    cases_list = list()
    death_list = list()
    for single in daterange(dd1, dd2):
        d_dates.append(single)
        sdate = date.strftime(single, dateformat)
        dates.append(sdate)
        try:
            si = resp.get("data").get(sdate).get(country_code).get(stringency)
            cases = resp.get("data").get(sdate).get(country_code).get(cases_str)
            cases_list.append(cases)
            ri, ri_h, ri_l = MathModel(stringency_index=si,
                                       contact_strategy=float(contact_strategy)).main_math
            si_list.append(si)
            ri_list.append(ri)
            ri_high.append(ri_h)
            ri_low.append(ri_l)
            death_list.append(math.log(cases))
        except AttributeError:
            app_log.info(f"No data for `{sdate}`")
            d_dates.pop()
            dates.pop()
    return dates, si_list, country_code, ri_list, cases_list, death_list


application = Flask(__name__, template_folder="templates", static_folder="static")

@application.route("/")
@application.route("/home")
def home():
    app_log.debug("Route `home` is called")
    return render_template("mainPage.html")

@application.route("/simple_chart")
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
    app_log.info(f"country `{country_code}`, from `{s_date}` to "
                 f"`{e_date}` strat {contact_strategy}")
    return jsonify(dates=dates, si=si, country=country, cases=cases,
                   log_cases=log_cases, ri=ri)


if __name__ == "__main__":
    app_log.info("flask app starts")
    application.run()
    app_log.info("flask app stops")
