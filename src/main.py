import requests
from datetime import timedelta, date
import json
from logger import log_settings
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
app_log = log_settings()


def daterange(start_date, end_date):
    for item in range(int((end_date - start_date).days)):
        yield start_date + timedelta(item)


dateformat = "%Y-%m-%d"
payload = dict()
headers = dict()


if __name__ == "__main__":
    date1 = "2020-09-01"
    date2 = "2020-09-10"
    country_code = "SVK"
    stringency = "stringency"
    dd1 = date.fromisoformat(date1)
    dd2 = date.fromisoformat(date2)
    url = f"https://covidtrackerapi.bsg.ox.ac.uk/api/v2/stringency/date-range/{date1}/{date2}"
    response = requests.request("GET", url, headers=headers, data=payload)
    resp = json.loads(response.text)
    dates = list()
    values = list()
    d_dates = list()
    for single in daterange(dd1, dd2):
        d_dates.append(single)
        sdate = date.strftime(single, dateformat)
        print(sdate, resp.get("data").get(sdate).get(country_code).get(stringency))
        dates.append(sdate)
        values.append(resp.get("data").get(sdate).get(country_code).get(stringency))
    print(dates, values, d_dates)
    arr1 = np.array(values)
    arr2 = np.array(d_dates)
    print(arr1, d_dates)
    fig1 = plt.figure(1, clear=True)
    ax1 = fig1.add_subplot(111)
    ax1.set_ylabel('Stringency')
    ax1.set_xlabel('date')
    ax1.set_title("Simple plot Stringency vs date")
    ax1.scatter(arr2, arr1, color='green', s=5, label='Str')
    ax1.set_xlim(dd1, dd2)
    ax1.legend()
    plt.gcf().autofmt_xdate()
    plt.grid()
    plt.show()
