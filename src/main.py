import requests
from datetime import timedelta, date
import json
import time
from logger import log_settings
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from math_model import MathModel

app_log = log_settings()

date1 = "2020-09-01"
date2 = "2020-10-29"
country_code = "SVK"
stringency = "stringency"
cases_str = "confirmed"
death_str = "deaths"
dateformat = "%Y-%m-%d"
payload = dict()
headers = dict()


def daterange(start_date, end_date):
    for item in range(int((end_date - start_date).days)):
        yield start_date + timedelta(item)


def take_date():
    dd1 = date.fromisoformat(date1)
    dd2 = date.fromisoformat(date2)
    url = f"https://covidtrackerapi.bsg.ox.ac.uk/api/v2/stringency/date-range/{date1}/{date2}"
    response = requests.request("GET", url, headers=headers, data=payload)
    resp = json.loads(response.text)
    dates = list()
    values = list()
    values_high = list()
    values_low = list()
    d_dates = list()
    ri_list = list()
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
            dead = resp.get("data").get(sdate).get(country_code).get(death_str)
            cases_list.append(cases)
            ri, ri_h, ri_l = MathModel(si).main_math
            si_list.append(si)
            values.append(ri)
            values_high.append(ri_h)
            values_low.append(ri_l)
            death_list.append(dead)
        except AttributeError:
            app_log.info(f"No data for `{sdate}`")
            d_dates.pop()
            dates.pop()
    return dates, si_list, country_code, values


if __name__ == "__main__":
    app_log.info("main starts")
    start_time = time.time()
    dd1 = date.fromisoformat(date1)
    dd2 = date.fromisoformat(date2)
    url = f"https://covidtrackerapi.bsg.ox.ac.uk/api/v2/stringency/date-range/{date1}/{date2}"
    response = requests.request("GET", url, headers=headers, data=payload)
    resp = json.loads(response.text)
    dates = list()
    values = list()
    values_high = list()
    values_low = list()
    d_dates = list()
    ri_list = list()
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
            dead = resp.get("data").get(sdate).get(country_code).get(death_str)
            cases_list.append(cases)
            ri, ri_h, ri_l = MathModel(si).main_math
            si_list.append(si)
            values.append(ri)
            values_high.append(ri_h)
            values_low.append(ri_l)
            death_list.append(dead)
        except AttributeError:
            app_log.info(f"No data for `{sdate}`")
            d_dates.pop()
            dates.pop()
    arr1 = np.array(values)
    arr2 = np.array(d_dates)
    arr3 = np.array(values_low)
    arr4 = np.array(values_high)
    arr5 = np.array(si_list)
    arr6 = np.array(cases_list)
    arr7 = np.array(death_list)
    app_log.info(f"Execution time: `{time.time() - start_time}` sec")
    # Figure is below
    fig1 = plt.figure(1, clear=True)
    ax1 = fig1.add_subplot(223)
    ax1.set_ylabel('Risk index')
    ax1.set_xlabel('date')
    ax1.set_title(f"Risk index vs date for {country_code}")
    ax1.scatter(arr2, arr1, color='green', s=15, label='RI')
    ax1.scatter(arr2, arr3, color='cyan', s=15, label='RI low')
    ax1.scatter(arr2, arr4, color='red', s=15, label='RI high')
    ax1.set_xlim(dd1, dd2)
    ax1.legend()
    plt.gcf().autofmt_xdate()
    plt.grid()
    ax2 = fig1.add_subplot(221)
    ax2.set_ylabel('Stringency')
    ax2.set_xlabel('date')
    ax2.set_title(f"Stringency vs date for {country_code}")
    ax2.scatter(arr2, arr5, color='green', s=15, label='SI')
    ax2.set_xlim(dd1, dd2)
    ax2.legend()
    plt.gcf().autofmt_xdate()
    plt.grid()
    ax3 = fig1.add_subplot(222)
    ax3.set_ylabel('Cases')
    ax3.set_xlabel('date')
    ax3.set_title(f"Cases vs date for {country_code}")
    ax3.scatter(arr2, arr6, color='green', s=15, label='Cases')
    ax3.set_xlim(dd1, dd2)
    ax3.legend()
    plt.gcf().autofmt_xdate()
    plt.grid()
    ax4 = fig1.add_subplot(224)
    ax4.set_ylabel('Death')
    ax4.set_xlabel('date')
    ax4.set_title(f"Deaths vs date for {country_code}")
    ax4.scatter(arr2, arr7, color='green', s=15, label='Death')
    ax4.set_xlim(dd1, dd2)
    ax4.legend()
    plt.gcf().autofmt_xdate()
    plt.grid()
    plt.show()
    app_log.info("main stops")
