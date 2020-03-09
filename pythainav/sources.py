from abc import ABC
from abc import abstractmethod
from functools import lru_cache
from typing import List

import dateparser
import requests

from furl import furl

from .nav import Nav


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
    def __init__(self, subscription_key):
        # TODO: WIP
        super().__init__()

    def get(self, fund: str):
        # TODO: WIP
        pass

    def list(self):
        # TODO: WIP
        pass
