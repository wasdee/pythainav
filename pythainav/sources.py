from abc import ABC
from abc import abstractmethod
from functools import lru_cache
from typing import List

import datetime
import dateparser
import requests

from furl import furl

from .nav import Nav
from .utils.date import date_range


class Source(ABC):
    @abstractmethod
    def get(self, fund: str):
        pass

    @abstractmethod
    def list(self):
        pass


class Finnomena(Source):
    base = furl("https://www.finnomena.com/fn3/api/fund/")

    def __init__(self):
        super().__init__()

    def _find_earliest(self, navs: List[Nav], date: str):
        navs.sort(key=lambda x: x.updated, reverse=True)

        date = dateparser.parse(date)
        for nav in navs:
            if date >= nav.updated:
                return nav
        else:
            return None

    def get(self, fund: str, date: str = None):

        if date:
            navs = self.get_range(fund)
            return self._find_earliest(navs, date)

        name2fund = self.list()

        url = self.base / "nav" / "latest"
        url.args["fund"] = name2fund[fund]["id"]

        # convert to str
        url = url.url

        nav = requests.get(url).json()
        nav = Nav(value=float(nav["value"]), updated=dateparser.parse(nav["nav_date"]), tags={"latest"}, fund=fund)
        return nav

    # cache here should be sensible since the fund is not regulary update
    # TODO: change or ttl cache with timeout = [1 hour, 1 day]
    @lru_cache(maxsize=1024)
    def get_range(self, fund: str, period="SI"):
        name2fund = self.list()

        url = self.base / "nav" / "q"
        url.args["fund"] = name2fund[fund]["id"]
        url.args["range"] = period

        # convert to str
        url = url.url

        navs_response = requests.get(url).json()

        navs = []
        for nav_resp in navs_response:
            nav = Nav(value=float(nav_resp["value"]), updated=dateparser.parse(nav_resp["nav_date"]), tags={}, fund=fund)
            nav.amount = nav_resp["amount"]
            navs.append(nav)

        return navs

    # cache here should be sensible since the fund is not regulary update
    # TODO: change or ttl cache with timeout = [1 hour, 1 day]
    @lru_cache(maxsize=1)
    def list(self):
        url = self.base / "public" / "list"
        url = url.url
        funds = requests.get(url).json()
        return {fund["short_code"]: fund for fund in funds}

    # def _list(self, )


class Sec(Source):
    base = furl("https://api.sec.or.th/")

    def __init__(self, subscription_key: dict = None):
        super().__init__()
        if subscription_key is None:
            raise ValueError("Missing subscription key")
        if not all([True if key in subscription_key else False for key in ['fundfactsheet', 'funddailyinfo']]):
            raise ValueError("subscription_key must contain 'fundfactsheet' and 'funddailyinfo' key")
        self.subscription_key = subscription_key
        self.headers = {
            'Content-Type': 'application/json',
        }
        self.base_url = {
            'fundfactsheet': self.base.copy().add(path=['FundFactsheet', 'fund']),
            'funddailyinfo': self.base.copy().add(path='FundDailyInfo'),
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get(self, fund: str, date: str = None):
        if date:
            if isinstance(date, str):
                query_date = dateparser.parse(date).date()
            elif isinstance(date, datetime.date):
                query_date = date
            elif isinstance(date, datetime.datetime):
                query_date = date.date()
        else:
            query_date = datetime.date.today()
        if not fund:
            raise ValueError("Must specify fund")
        list_fund = self.search(fund)
        if list_fund:
            fund_info = list_fund.pop(0)
            fund_id = fund_info['proj_id']
            nav = self.get_nav_from_fund_id(fund_id, query_date)
            if isinstance(nav, Nav):
                nav.fund = fund_info['proj_abbr_name']
                if query_date == datetime.date.today():
                    nav.tags = {"latest"}
                return nav
            else:
                return nav
        else:
            # Fund not found
            return []

    def get_range(self, fund: str, period="SI"):
        list_fund = self.search(fund)
        if list_fund:
            fund_info = list_fund.pop(0)
            today = datetime.date.today()
            if period == "SI":
                if fund_info['regis_date'] != "-":
                    inception_date = dateparser.parse(fund_info['regis_date']).date()
                    data_date = date_range(inception_date, today)
                else:
                    date_date = [today]
            else:
                query_date = dateparser.parse(period).date()
                data_date = date_range(query_date, today)
            list_nav = []
            # Remove weekend
            data_date = [dd for dd in date_date if dd.isoweekday() not in [6, 7]]
            for dd in data_date:
                nav = self.get_nav_from_fund_id(fund, dd)
                if nav:
                    list_nav.append(nav)
            return list_nav
        else:
            # Fund not found
            return []

    @lru_cache(maxsize=1024)
    def get_nav_from_fund_id(self, fund_id: str, nav_date: datetime.date):
        url = self.base_url['funddailyinfo'].copy().add(path=[fund_id, 'dailynav', nav_date.isoformat()]).url
        headers = self.headers
        headers.update({'Ocp-Apim-Subscription-Key': self.subscription_key['funddailyinfo']})
        response = self.session.get(url, headers=headers)
        # check status code
        response.raise_for_status()
        if response.status_code == 200:
            result = response.json()
            # Multi class fund
            if float(result['last_val']) == 0.0 and float(result['previous_val']) == 0:
                remark_en = result['amc_info'][0]['remark_en']
                multi_class_nav = {k.strip(): float(v) for x in remark_en.split("/") for k, v in [x.split("=")]}
                list_nav = []
                for fund_name, nav_val in multi_class_nav.items():
                    n = Nav(value=float(nav_val), updated=dateparser.parse(result["nav_date"]), tags={}, fund=fund_name)
                    n.amount = result['net_asset']
                    list_nav.append(n)
                return list_nav
            else:
                n = Nav(value=float(result["last_val"]), updated=dateparser.parse(result["nav_date"]), tags={}, fund=fund_id)
                n.amount = result['net_asset']
                return n
        # No content
        elif response.status_code == 204:
            return []

    @lru_cache(maxsize=1024)
    def list(self):
        return self.search_fund(name="")

    def search(self, name: str):
        result = self.search_fund(name)
        if len(result) == 0:
            result = self.search_class_fund(name)
        return result

    @lru_cache(maxsize=1024)
    def search_fund(self, name: str):
        url = self.base_url['fundfactsheet'].url
        headers = self.headers
        headers.update({'Ocp-Apim-Subscription-Key': self.subscription_key['fundfactsheet']})
        response = self.session.post(url, headers=headers, json={'name': name})
        # check status code
        response.raise_for_status()
        if response.status_code == 200:
            return response.json()
        # No content
        elif response.status_code == 204:
            return []

    @lru_cache(maxsize=1024)
    def search_class_fund(self, name: str):
        url = self.base_url['fundfactsheet'].copy().add(path='class_fund').url
        headers = self.headers
        headers.update({'Ocp-Apim-Subscription-Key': self.subscription_key['fundfactsheet']})
        response = self.session.post(url, headers=headers, json={'name': name})
        # check status code
        response.raise_for_status()
        if response.status_code == 200:
            return response.json()
        # No content
        elif response.status_code == 204:
            return []
