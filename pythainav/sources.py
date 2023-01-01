from typing import List

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


import datetime
from abc import ABC, abstractmethod
from functools import lru_cache

import dateparser
import requests
from furl import furl

from .nav import Nav
from .utils.date import convert_buddhist_to_gregorian, date_range


class Source(ABC):
    @abstractmethod
    def get(self, fund: str):
        pass

    @abstractmethod
    def list(self):
        pass


class Finnomena(Source):
    base = furl("https://www.finnomena.com/fn3/api/fund/")
    base_v2 = furl("https://www.finnomena.com/fn3/api/fund/v2/")

    def __init__(self):
        super().__init__()

    def _find_earliest(self, navs: List[Nav], date: str):
        navs.sort(key=lambda x: x.updated, reverse=True)

        date = dateparser.parse(date)
        for nav in navs:
            if date >= nav.updated:
                return nav
        return None

    def get(self, fund: str, date: str = None):
        fund = fund.lower()

        if date:
            navs = self.get_range(fund)
            return self._find_earliest(navs, date)

        name2fund = self.list()

        url = self.base / "nav" / "latest"
        url.args["fund"] = name2fund[fund]["id"]

        # convert to str
        url = url.url

        nav = requests.get(url).json()
        nav = Nav(
            value=float(nav["value"]),
            updated=datetime.datetime.strptime(nav["nav_date"], "%Y-%m-%d"),
            tags={"latest"},
            fund=fund,
        )
        return nav

    # cache here should be sensible since the fund is not regulary update
    # TODO: change or ttl cache with timeout = [1 hour, 1 day]
    @lru_cache(maxsize=1024)
    def get_range_v1(self, fund: str, period="SI"):
        name2fund = self.list()

        url = self.base / "nav" / "q"
        url.args["fund"] = name2fund[fund]["id"]
        url.args["range"] = period

        # convert to str
        url = url.url

        navs_response = requests.get(url).json()

        navs = []
        for nav_resp in navs_response:
            nav = Nav(
                value=float(nav_resp["value"]),
                updated=dateparser.parse(nav_resp["nav_date"]),
                tags={},
                fund=fund,
            )
            nav.amount = nav_resp["amount"]
            navs.append(nav)

        return navs

    # cache here should be sensible since the fund is not regulary update
    # TODO: change or ttl cache with timeout = [1 hour, 1 day]
    @lru_cache(maxsize=1024)
    def get_range(
        self,
        fund: str,
        range: Literal[
            "1D", "1W", "1M", "6M", "YTD", "1Y", "3Y", "5Y", "10Y", "MAX"
        ] = "1Y",
    ):
        name2fund = self.list()

        # /fn3/api/fund/v2/ public/funds/F00000IT9T/nav/q
        url = (
            self.base_v2
            / "public"
            / "funds"
            / name2fund[fund]["id"]
            / "nav"
            / "q"
        )
        url.args["range"] = range

        # convert to str
        url = url.url

        navs_response = requests.get(url).json()

        if not navs_response["status"]:
            raise Exception(f"response to {url} is invalid")

        navs = []
        for nav_resp in navs_response["data"]["navs"]:
            date = dateparser.parse(nav_resp["date"])
            date = date.replace(tzinfo=None)
            nav = Nav(
                value=float(nav_resp["value"]),
                updated=date,
                tags={},
                fund=fund,
            )
            nav.amount = nav_resp["amount"]
            navs.append(nav)

        return navs

    # cache here should be sensible since the fund is not regulary update
    # TODO: change or ttl cache with timeout = [1 hour, 1 day]
    # TODO: New API exists /fn3/api/fund/public/filter/overview
    @lru_cache(maxsize=1)
    def list(self):
        url = self.base / "public" / "list"
        url = url.url
        funds = requests.get(url).json()
        return {fund["short_code"].lower(): fund for fund in funds}

    # def _list(self, )


class Sec(Source):
    base = furl("https://api.sec.or.th/")

    def __init__(self, subscription_key: dict = None):
        super().__init__()
        if subscription_key is None:
            # TODO: Create specific exception for this
            raise ValueError("Missing subscription key")
        if not all(
            [
                True if key in subscription_key else False
                for key in ["fundfactsheet", "funddailyinfo"]
            ]
        ):
            raise ValueError(
                "subscription_key must contain 'fundfactsheet' and 'funddailyinfo' key"
            )
        self.subscription_key = subscription_key
        self.headers = {
            "Content-Type": "application/json",
        }
        self.base_url = {
            "fundfactsheet": self.base.copy().add(
                path=["FundFactsheet", "fund"]
            ),
            "funddailyinfo": self.base.copy().add(path="FundDailyInfo"),
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def __get_api_data(
        self, url, headers=None, subscription_key="fundfactsheet"
    ):
        if headers is None:
            headers = self.headers
        headers.update(
            {
                "Ocp-Apim-Subscription-Key": self.subscription_key[
                    subscription_key
                ]
            }
        )
        response = self.session.get(url, headers=headers)
        # check status code
        response.raise_for_status()
        if response.status_code == 200:
            if response.headers["content-length"] == "0":
                return None
            return response.json()
        # No content
        elif response.status_code == 204:
            return None

    def get(self, fund: str, date: str = None):
        if date:
            if isinstance(date, str):
                query_date = dateparser.parse(date).date()
            elif isinstance(date, datetime.date):
                query_date = date
            elif isinstance(date, datetime.datetime):
                query_date = date.date()
        else:
            # TODO: Upgrade to smarter https://stackoverflow.com/questions/2224742/most-recent-previous-business-day-in-python
            # PS. should i add pandas as dep? it's so largeee.
            query_date = last_bus_day = datetime.date.today()
            wk_day = datetime.date.weekday(last_bus_day)
            if wk_day > 4:  # if it's Saturday or Sunday
                last_bus_day = last_bus_day - datetime.timedelta(
                    days=wk_day - 4
                )  # then make it Friday
            query_date = last_bus_day

        if not fund:
            raise ValueError("Must specify fund")

        list_fund = self.search(fund)
        if list_fund:
            fund_info = list_fund.pop(0)
            fund_id = fund_info["proj_id"]
            nav = self.get_nav_from_fund_id(fund_id, query_date)

            if isinstance(nav, Nav):
                nav.fund = fund_info["proj_abbr_name"]
                if query_date == datetime.date.today():
                    nav.tags = {"latest"}
                return nav
            else:
                return nav
        else:
            # Fund not found
            # due to query_date is a week day that also a holiday
            return None

    def get_range(self, fund: str, period="SI"):
        list_fund = self.search(fund)
        if list_fund:
            fund_info = list_fund.pop(0)
            today = datetime.date.today()
            if period == "SI":
                if fund_info["regis_date"] != "-":
                    inception_date = dateparser.parse(
                        fund_info["regis_date"]
                    ).date()
                    data_date = date_range(inception_date, today)
                else:
                    date_date = [today]
            else:
                query_date = dateparser.parse(period).date()
                data_date = date_range(query_date, today)
            list_nav = []
            # Remove weekend
            data_date = [
                dd for dd in date_date if dd.isoweekday() not in [6, 7]
            ]
            for dd in data_date:
                nav = self.get_nav_from_fund_id(fund, dd)
                if nav:
                    list_nav.append(nav)
            return list_nav
        else:
            # Fund not found
            return None

    @lru_cache(maxsize=1024)
    def get_nav_from_fund_id(self, fund_id: str, nav_date: datetime.date):
        url = (
            self.base_url["funddailyinfo"]
            .copy()
            .add(path=[fund_id, "dailynav", nav_date.isoformat()])
            .url
        )
        headers = self.headers
        headers.update(
            {
                "Ocp-Apim-Subscription-Key": self.subscription_key[
                    "funddailyinfo"
                ]
            }
        )
        response = self.session.get(url, headers=headers)
        # check status code
        response.raise_for_status()
        if response.status_code == 200:
            if response.headers["content-length"] == "0":
                raise requests.exceptions.ConnectionError("No data received")
            result = response.json()
            # Multi class fund
            if (
                float(result["last_val"]) == 0.0
                and float(result["previous_val"]) == 0
            ):
                remark_en = result["amc_info"][0]["remark_en"]
                multi_class_nav = {
                    k.strip(): float(v)
                    for x in remark_en.split("/")
                    for k, v in [x.split("=")]
                }
                list_nav = []
                for fund_name, nav_val in multi_class_nav.items():
                    n = Nav(
                        value=float(nav_val),
                        updated=dateparser.parse(result["nav_date"]),
                        tags={},
                        fund=fund_name,
                    )
                    n.amount = result["net_asset"]
                    list_nav.append(n)
                return list_nav
            else:
                n = Nav(
                    value=float(result["last_val"]),
                    updated=dateparser.parse(result["nav_date"]),
                    tags={},
                    fund=fund_id,
                )
                n.amount = result["net_asset"]
                return n
        # No content
        elif response.status_code == 204:
            return None

    @lru_cache(maxsize=1024)
    def list(self):
        return self.search_fund(name="")

    def search(self, name: str):
        result = self.search_fund(name)
        if result is None:
            result = self.search_class_fund(name)
        return result

    @lru_cache(maxsize=1024)
    def search_fund(self, name: str):
        url = self.base_url["fundfactsheet"].url
        headers = self.headers
        headers.update(
            {
                "Ocp-Apim-Subscription-Key": self.subscription_key[
                    "fundfactsheet"
                ]
            }
        )
        response = self.session.post(url, headers=headers, json={"name": name})
        # check status code
        response.raise_for_status()
        if response.status_code == 200:
            if response.headers["content-length"] == "0":
                raise requests.exceptions.ConnectionError("No data received")
            return response.json()
        # No content
        elif response.status_code == 204:
            return None

    @lru_cache(maxsize=1024)
    def search_class_fund(self, name: str):
        url = self.base_url["fundfactsheet"].copy().add(path="class_fund").url
        headers = self.headers
        headers.update(
            {
                "Ocp-Apim-Subscription-Key": self.subscription_key[
                    "fundfactsheet"
                ]
            }
        )
        response = self.session.post(url, headers=headers, json={"name": name})
        # check status code
        response.raise_for_status()
        if response.status_code == 200:
            if response.headers["content-length"] == "0":
                raise requests.exceptions.ConnectionError("No data received")
            return response.json()
        # No content
        elif response.status_code == 204:
            return None

    def list_amc(self):
        url = self.base_url["fundfactsheet"].copy().add(path="amc").url
        result = self.__get_api_data(url)
        return result

    def list_fund_under_amc(self, amc_id):
        if amc_id is None and not amc_id:
            raise ValueError("Missing amc_id")
        url = (
            self.base_url["fundfactsheet"].copy().add(path=["amc", amc_id]).url
        )
        result = self.__get_api_data(url)
        return result

    def get_fund_factsheet_url(self, fund_id):
        if not fund_id:
            raise ValueError("Must specify fund")
        url = (
            self.base_url["fundfactsheet"]
            .copy()
            .add(path=[fund_id, "URLs"])
            .url
        )
        result = self.__get_api_data(url)
        return result

    def get_fund_ipo(self, fund_id):
        if not fund_id:
            raise ValueError("Must specify fund")
        url = (
            self.base_url["fundfactsheet"].copy().add(path=[fund_id, "IPO"]).url
        )
        result = self.__get_api_data(url)
        return result

    def get_fund_investment(self, fund_id):
        if not fund_id:
            raise ValueError("Must specify fund")
        url = (
            self.base_url["fundfactsheet"]
            .copy()
            .add(path=[fund_id, "investment"])
            .url
        )
        result = self.__get_api_data(url)
        return result

    def get_fund_project_type(self, fund_id):
        if not fund_id:
            raise ValueError("Must specify fund")
        url = (
            self.base_url["fundfactsheet"]
            .copy()
            .add(path=[fund_id, "project_type"])
            .url
        )
        result = self.__get_api_data(url)
        return result

    def get_fund_policy(self, fund_id):
        if not fund_id:
            raise ValueError("Must specify fund")
        url = (
            self.base_url["fundfactsheet"]
            .copy()
            .add(path=[fund_id, "policy"])
            .url
        )
        result = self.__get_api_data(url)
        if "investment_policy_desc" in result and len(
            result["investment_policy_desc"]
        ):
            result["investment_policy_desc"] = base64.b64decode(
                result["investment_policy_desc"]
            ).decode("utf-8")
        return result

    def get_fund_specification(self, fund_id):
        if not fund_id:
            raise ValueError("Must specify fund")
        url = (
            self.base_url["fundfactsheet"]
            .copy()
            .add(path=[fund_id, "specification"])
            .url
        )
        result = self.__get_api_data(url)
        return result

    def get_fund_feeder_fund(self, fund_id):
        if not fund_id:
            raise ValueError("Must specify fund")
        url = (
            self.base_url["fundfactsheet"]
            .copy()
            .add(path=[fund_id, "feeder_fund"])
            .url
        )
        result = self.__get_api_data(url)
        return result

    def get_fund_redemption(self, fund_id):
        if not fund_id:
            raise ValueError("Must specify fund")
        url = (
            self.base_url["fundfactsheet"]
            .copy()
            .add(path=[fund_id, "redemption"])
            .url
        )
        result = self.__get_api_data(url)
        return result

    def get_fund_suitability(self, fund_id):
        if not fund_id:
            raise ValueError("Must specify fund")
        url = (
            self.base_url["fundfactsheet"]
            .copy()
            .add(path=[fund_id, "suitability"])
            .url
        )
        result = self.__get_api_data(url)
        for key in [
            "fund_suitable_desc",
            "fund_not_suitable_desc",
            "important_notice",
            "risk_spectrum_desc",
        ]:
            if key in result:
                result[key] = base64.b64decode(result[key]).decode("utf-8")
        return result

    def get_fund_risk(self, fund_id):
        if not fund_id:
            raise ValueError("Must specify fund")
        url = (
            self.base_url["fundfactsheet"]
            .copy()
            .add(path=[fund_id, "risk"])
            .url
        )
        result = self.__get_api_data(url)
        return result

    def get_fund_asset(self, fund_id):
        if not fund_id:
            raise ValueError("Must specify fund")
        url = (
            self.base_url["fundfactsheet"]
            .copy()
            .add(path=[fund_id, "asset"])
            .url
        )
        result = self.__get_api_data(url)
        return result

    def get_fund_turnover_ratio(self, fund_id):
        if not fund_id:
            raise ValueError("Must specify fund")
        url = (
            self.base_url["fundfactsheet"]
            .copy()
            .add(path=[fund_id, "turnover_ratio"])
            .url
        )
        result = self.__get_api_data(url)
        return result

    def get_fund_return(self, fund_id):
        if not fund_id:
            raise ValueError("Must specify fund")
        url = (
            self.base_url["fundfactsheet"]
            .copy()
            .add(path=[fund_id, "return"])
            .url
        )
        result = self.__get_api_data(url)
        return result

    def get_fund_buy_and_hold(self, fund_id):
        if not fund_id:
            raise ValueError("Must specify fund")
        url = (
            self.base_url["fundfactsheet"]
            .copy()
            .add(path=[fund_id, "buy_and_hold"])
            .url
        )
        result = self.__get_api_data(url)
        return result

    def get_fund_benchmark(self, fund_id):
        if not fund_id:
            raise ValueError("Must specify fund")
        url = (
            self.base_url["fundfactsheet"]
            .copy()
            .add(path=[fund_id, "benchmark"])
            .url
        )
        result = self.__get_api_data(url)
        return result

    def get_fund_compare(self, fund_id):
        if not fund_id:
            raise ValueError("Must specify fund")
        url = (
            self.base_url["fundfactsheet"]
            .copy()
            .add(path=[fund_id, "fund_compare"])
            .url
        )
        result = self.__get_api_data(url)
        return result

    def get_class_fund(self, fund_id):
        if not fund_id:
            raise ValueError("Must specify fund")
        url = (
            self.base_url["fundfactsheet"]
            .copy()
            .add(path=[fund_id, "class_fund"])
            .url
        )
        result = self.__get_api_data(url)
        return result

    def get_fund_performance(self, fund_id):
        if not fund_id:
            raise ValueError("Must specify fund")
        url = (
            self.base_url["fundfactsheet"]
            .copy()
            .add(path=[fund_id, "performance"])
            .url
        )
        result = self.__get_api_data(url)
        return result

    def get_fund_5yearlost(self, fund_id):
        if not fund_id:
            raise ValueError("Must specify fund")
        url = (
            self.base_url["fundfactsheet"]
            .copy()
            .add(path=[fund_id, "5YearLost"])
            .url
        )
        result = self.__get_api_data(url)
        return result

    def get_fund_dividend_policy(self, fund_id):
        if not fund_id:
            raise ValueError("Must specify fund")
        url = (
            self.base_url["fundfactsheet"]
            .copy()
            .add(path=[fund_id, "dividend"])
            .url
        )
        result = self.__get_api_data(url)
        for record in result:
            if "dividend_details" in record:
                for dividend_record in record["dividend_details"]:
                    if dividend_record["book_closing_date"] != "-":
                        dividend_record["book_closing_date"] = (
                            convert_buddhist_to_gregorian(
                                dividend_record["book_closing_date"]
                            )
                            .date()
                            .isoformat()
                        )
                    if dividend_record["payment_date"] != "-":
                        dividend_record["payment_date"] = (
                            convert_buddhist_to_gregorian(
                                dividend_record["payment_date"]
                            )
                            .date()
                            .isoformat()
                        )
        return result

    def get_fund_fee(self, fund_id):
        if not fund_id:
            raise ValueError("Must specify fund")
        url = (
            self.base_url["fundfactsheet"].copy().add(path=[fund_id, "fee"]).url
        )
        result = self.__get_api_data(url)
        return result

    def get_fund_involveparty(self, fund_id):
        if not fund_id:
            raise ValueError("Must specify fund")
        url = (
            self.base_url["fundfactsheet"]
            .copy()
            .add(path=[fund_id, "InvolveParty"])
            .url
        )
        result = self.__get_api_data(url)
        for record in result:
            if "effective_date" in record and record["effective_date"] != "-":
                record["effective_date"] = (
                    convert_buddhist_to_gregorian(record["effective_date"])
                    .date()
                    .isoformat()
                )
        return result

    def get_fund_port(self, fund_id, period):
        if not fund_id:
            raise ValueError("Must specify fund")
        url = (
            self.base_url["fundfactsheet"]
            .copy()
            .add(path=[fund_id, "FundPort", period])
            .url
        )
        result = self.__get_api_data(url)
        return result

    def get_fund_full_port(self, fund_id, period):
        if not fund_id:
            raise ValueError("Must specify fund")
        url = (
            self.base_url["fundfactsheet"]
            .copy()
            .add(path=[fund_id, "FundPort", period])
            .url
        )
        result = self.__get_api_data(url)
        return result

    def get_fund_top5_port(self, fund_id, period):
        if not fund_id:
            raise ValueError("Must specify fund")
        url = (
            self.base_url["fundfactsheet"]
            .copy()
            .add(path=[fund_id, "FundTop5", period])
            .url
        )
        result = self.__get_api_data(url)
        return result

    def get_fund_dividend(self, fund_id):
        if not fund_id:
            raise ValueError("Must specify fund")
        url = (
            self.base_url["funddailyinfo"]
            .copy()
            .add(path=[fund_id, "dividend"])
            .url
        )
        result = self.__get_api_data(url, subscription_key="funddailyinfo")
        return result

    def get_amc_submit_dailyinfo(self):
        url = self.base_url["funddailyinfo"].copy().add(path=["amc"]).url
        result = self.__get_api_data(url, subscription_key="funddailyinfo")
        return result
