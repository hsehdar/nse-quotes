#!/usr/bin/env python3
import requests
import sys
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from dateutil.rrule import MO, TU, WE, TH, FR, SA, SU
from urllib.error import HTTPError

class Utils:
    dateFormat = "%d-%m-%Y"

    def last_week_date(self, dayOfTheWeek=None, dateToUse=datetime.today()):
        relativeDeltaWeeks=-1
        if not dateToUse:
            dateToUse=datetime.today()
        if not dayOfTheWeek:
            dayOfTheWeek = 'MO'
        if dateToUse.weekday() == 0:
            relativeDeltaWeeks=-2
        match dayOfTheWeek:
            case "MO":
                return datetime.strftime(dateToUse + relativedelta(weekday=MO(relativeDeltaWeeks)), self.dateFormat)
            case "TU":
                return datetime.strftime(dateToUse + relativedelta(weekday=TU(relativeDeltaWeeks)), self.dateFormat)
            case "WE":
                return datetime.strftime(dateToUse + relativedelta(weekday=WE(relativeDeltaWeeks)), self.dateFormat)
            case "TH":
                return datetime.strftime(dateToUse + relativedelta(weekday=TH(relativeDeltaWeeks)), self.dateFormat)
            case "FR":
                return datetime.strftime(dateToUse + relativedelta(weekday=FR(relativeDeltaWeeks)), self.dateFormat)
            case "SA":
                return datetime.strftime(dateToUse + relativedelta(weekday=SA(relativeDeltaWeeks)), self.dateFormat)
            case "SU":
                return datetime.strftime(dateToUse + relativedelta(weekday=SU(relativeDeltaWeeks)), self.dateFormat)
            case _:
                return datetime.strftime(dateToUse, self.dateFormat)

    def format_str_to_date(self, givenDate=None):
        dateFormatState = True
        try:
            dateFormatState = bool(datetime.strptime(str(givenDate), self.dateFormat))
        except ValueError:
            dateFormatState = False
        if dateFormatState:
            return datetime.strftime(
                datetime.strptime(givenDate, self.dateFormat), self.dateFormat
            )
        else:
            return datetime.strftime(date.today(), self.dateFormat)

class NSESession:
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
        "accept-language": "en,gu;q=0.9,hi;q=0.8",
        "accept-encoding": "gzip, deflate, br",
    }
    baseurl = "https://www.nseindia.com/"

    def __init__(self):
        try:
            self.session = requests.Session()
            request = self.session.get(self.baseurl, headers=self.headers, timeout=5)
            self.cookies = dict(request.cookies)
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"Other error occurred: {err}")

    def check_symbol(self, symbol):
        symbolExistence = False
        try:
            symbolExistence = (
                "No Data Found"
                not in self.session.get(
                    self.baseurl + "api/equity-meta-info?symbol=" + symbol,
                    headers=self.headers,
                    timeout=5,
                ).text
            )
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"Other error occurred: {err}")
        return symbolExistence

    def get_symbol_series(self, symbol):
        try:
            return (
                (
                    self.session.get(
                        self.baseurl
                        + "/api/historical/cm/equity/series?symbol="
                        + symbol,
                        headers=self.headers,
                        timeout=5,
                    ).text
                )
                .replace('{"data":', "")
                .replace("}", "")
                .replace('"', "%22")
                .replace(" ", "")
            )
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"Other error occurred: {err}")

    def get_symbol_quote(self, symbol=None):
        symbol or sys.exit("Give me at least one symbol to get you the details.")
        if not self.check_symbol(symbol):
            return False
        try:
            return self.session.get(
                self.baseurl + "api/quote-equity?symbol=" + symbol,
                headers=self.headers,
                timeout=5,
            ).text
        except HTTPError as http_err:
            symbolExistence = False
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            symbolExistence = False
            print(f"Other error occurred: {err}")

    def get_symbol_quote_history(self, symbol=None, startDate=None, endDate=None):
        symbol or sys.exit("Give me at least one symbol to get you the details.")
        utils = Utils()
        if not startDate and not endDate:
            startDate = utils.last_week_date(None, None)
            endDate = utils.last_week_date('FR', None)
        if not endDate:
            endDate = utils.last_week_date('FR', None)
        if not startDate:
            startDate = utils.last_week_date(None, datetime.strptime(endDate, utils.dateFormat))
        if not self.check_symbol(symbol):
            return False
        startDate, endDate = utils.format_str_to_date(startDate), utils.format_str_to_date(endDate)
        if datetime.strptime(startDate, utils.dateFormat).date() >= datetime.strptime(endDate, utils.dateFormat).date():
            startDate, endDate = endDate, startDate
        try:
            return self.session.get(
                self.baseurl
                + "/api/historical/cm/equity?symbol="
                + symbol
                + "&series="
                + self.get_symbol_series(symbol)
                + "&from="
                + startDate
                + "&to="
                + endDate,
                headers=self.headers,
                timeout=5,
            ).text
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"Other error occurred: {err}")