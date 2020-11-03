import requests
from datetime import timedelta, date
import json
from pprint import pprint as pp


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
    print(dd1, dd2)
    url = f"https://covidtrackerapi.bsg.ox.ac.uk/api/v2/stringency/date-range/{date1}/{date2}"
    response = requests.request("GET", url, headers=headers, data=payload)
    resp = json.loads(response.text)
    pp(resp.get("scale"))
    pp(resp.get("data").get("2020-09-01").get("SVK").get("stringency"))
    for single in daterange(dd1, dd2):
        sdate = date.strftime(single, dateformat)
        print(resp.get("data").get(sdate).get(country_code).get(stringency))