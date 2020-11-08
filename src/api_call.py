import requests
from datetime import timedelta, date
import json
from logger import log_settings
import math
from math_model import MathModel

app_log = log_settings()

# date1 = "2020-10-20"
# date2 = "2020-10-29"
# country_code = "SVK"
stringency = "stringency"
cases_str = "confirmed"
death_str = "deaths"
dateformat = "%Y-%m-%d"
payload = dict()
headers = dict()


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


if __name__ == "__main__":
    pass
