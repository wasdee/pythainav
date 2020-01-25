from abc import ABC
from abc import abstractmethod
from functools import lru_cache

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

    def get(self, fund: str):
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
