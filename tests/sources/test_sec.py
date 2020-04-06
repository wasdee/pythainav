import datetime
import json
import re
import typing

from dataclasses import dataclass

import dateparser
import pytest
import requests

import httpretty
import mock

from pythainav.nav import Nav
from pythainav.sources import Sec

from .helpers.sec_data import setup_sec_data


@dataclass
class SecData:
    search_fund_data: "typing.Any" = object()
    search_class_fund_data: "typing.Any" = object()
    dailynav_data: "typing.Any" = object()
    multi_class_dailynav_data: "typing.Any" = object()
    subscription_key: "typing.Any" = object()
    sec: "typing.Any" = object()
    nav_date: "typing.Any" = object()


@pytest.fixture
def sec_data():
    sd = SecData()
    setup_sec_data(sd, httpretty)
    sd.subscription_key = {"fundfactsheet": "fact_key", "funddailyinfo": "daily_key"}
    sd.sec = Sec(subscription_key=sd.subscription_key)
    sd.nav_date = datetime.date(2020, 1, 1)
    yield sd
    # teardown
    httpretty.disable()
    httpretty.reset()


def test_no_subscription_key():
    with pytest.raises(ValueError):
        Sec()


def test_subscription_key_is_none():
    subscription_key = None
    with pytest.raises(ValueError):
        Sec(subscription_key)

    with pytest.raises(ValueError):
        Sec(subscription_key=subscription_key)


def test_subscription_key_missing_key():

    with pytest.raises(ValueError):
        Sec(subscription_key={"wrong_name": "some_key"})

    with pytest.raises(ValueError):
        Sec(subscription_key={"fundfactsheet": "some_key"})

    with pytest.raises(ValueError):
        Sec(subscription_key={"funddailyinfo": "some_key"})

    test_sec = Sec(subscription_key={"fundfactsheet": "some_key", "funddailyinfo": "some_key"})
    assert list(test_sec.subscription_key.keys()) == ["fundfactsheet", "funddailyinfo"]


#
#   search_fund
#
def test_search_fund_setting_headers(sec_data):
    sec_data.sec.search_fund("FUND")

    # contain Ocp-Apim-Subscription-Key in header
    assert "Ocp-Apim-Subscription-Key" in httpretty.last_request().headers
    assert httpretty.last_request().headers["Ocp-Apim-Subscription-Key"] == sec_data.subscription_key["fundfactsheet"]


def test_search_fund_invalid_key(sec_data):
    httpretty.reset()
    error_responses = [
        httpretty.Response(
            status=401,
            body=json.dumps(
                {
                    "statusCode": 401,
                    "message": "Access denied due to invalid subscription key. Make sure to provide a valid key for an active subscription.",
                }
            ),
        )
    ]

    httpretty.register_uri(httpretty.POST, "https://api.sec.or.th/FundFactsheet/fund", responses=error_responses)
    with pytest.raises(requests.exceptions.HTTPError):
        sec_data.sec.search_fund("FUND")


def test_search_fund_success_with_content(sec_data):
    # status code 200
    result = sec_data.sec.search_fund("FUND")

    assert result == sec_data.search_fund_data


def test_search_fund_no_content(sec_data):
    # status code 204
    httpretty.reset()

    httpretty.register_uri(httpretty.POST, "https://api.sec.or.th/FundFactsheet/fund", status=204)
    result = sec_data.sec.search_fund("FUND")
    assert result == []


#
#   search_class_fund
#
def test_search_class_fund_setting_headers(sec_data):
    sec_data.sec.search_class_fund("FUND")

    # contain Ocp-Apim-Subscription-Key in header
    assert "Ocp-Apim-Subscription-Key" in httpretty.last_request().headers
    assert httpretty.last_request().headers["Ocp-Apim-Subscription-Key"] == sec_data.subscription_key["fundfactsheet"]


def test_search_class_fund_invalid_key(sec_data):
    httpretty.reset()
    error_responses = [
        httpretty.Response(
            status=401,
            body=json.dumps(
                {
                    "statusCode": 401,
                    "message": "Access denied due to invalid subscription key. Make sure to provide a valid key for an active subscription.",
                }
            ),
        )
    ]

    httpretty.register_uri(httpretty.POST, "https://api.sec.or.th/FundFactsheet/fund/class_fund", responses=error_responses)
    with pytest.raises(requests.exceptions.HTTPError):
        sec_data.sec.search_class_fund("FUND")


def test_search_class_fund_success_with_content(sec_data):
    # status code 200
    result = sec_data.sec.search_class_fund("FUND")

    assert result == sec_data.search_class_fund_data


def test_search_class_fund_no_content(sec_data):
    # status code 204
    httpretty.reset()

    httpretty.register_uri(httpretty.POST, "https://api.sec.or.th/FundFactsheet/fund/class_fund", status=204)
    result = sec_data.sec.search_class_fund("FUND")
    assert result == []


#
#   search
#
@mock.patch("pythainav.sources.Sec.search_class_fund")
@mock.patch("pythainav.sources.Sec.search_fund")
def test_search_result(mock_search_fund, mock_search_class_fund, sec_data):
    # search_fund found fund
    mock_search_fund.return_value = sec_data.search_fund_data
    result = sec_data.sec.search("FUND")
    assert result == sec_data.search_fund_data

    # search_fund return empty
    mock_search_fund.return_value = []
    mock_search_class_fund.return_value = sec_data.search_class_fund_data
    result = sec_data.sec.search("FUND")
    assert mock_search_class_fund.called
    assert result == sec_data.search_class_fund_data

    # both return empty
    mock_search_fund.return_value = []
    mock_search_class_fund.return_value = []
    result = sec_data.sec.search("FUND")
    assert result == []


#
#   list
#
def test_list_result(sec_data):
    result = sec_data.sec.list()

    assert len(result) == len(sec_data.search_fund_data)


#
#   get_nav_from_fund_id
#
def test_get_nav_from_fund_id_setting_headers(sec_data):
    sec_data.sec.get_nav_from_fund_id("FUND_ID", sec_data.nav_date)

    # contain Ocp-Apim-Subscription-Key in header
    assert "Ocp-Apim-Subscription-Key" in httpretty.last_request().headers
    assert httpretty.last_request().headers["Ocp-Apim-Subscription-Key"] == sec_data.subscription_key["funddailyinfo"]


def test_get_nav_from_fund_id_invalid_key(sec_data):
    httpretty.reset()
    error_responses = [
        httpretty.Response(
            status=401,
            body=json.dumps(
                {
                    "statusCode": 401,
                    "message": "Access denied due to invalid subscription key. Make sure to provide a valid key for an active subscription.",
                }
            ),
        )
    ]

    httpretty.register_uri(
        httpretty.GET, re.compile("https://api.sec.or.th/FundDailyInfo/.*/dailynav/.*"), responses=error_responses
    )
    with pytest.raises(requests.exceptions.HTTPError):
        sec_data.sec.get_nav_from_fund_id("FUND_ID", sec_data.nav_date)


def test_get_nav_from_fund_id_success_with_content(sec_data):
    # status code 200
    expect_return = Nav(
        value=float(sec_data.dailynav_data["last_val"]),
        updated=dateparser.parse(sec_data.dailynav_data["nav_date"]),
        tags={},
        fund="FUND_ID",
    )

    result = sec_data.sec.get_nav_from_fund_id("FUND_ID", sec_data.nav_date)

    assert result == expect_return


def test_get_nav_from_fund_id_no_content(sec_data):
    # status code 204
    httpretty.reset()

    httpretty.register_uri(httpretty.GET, re.compile("https://api.sec.or.th/FundDailyInfo/.*/dailynav/.*"), status=204)
    result = sec_data.sec.get_nav_from_fund_id("FUND_ID", sec_data.nav_date)
    assert result is None


def test_get_nav_from_fund_id_multi_class(sec_data):
    httpretty.reset()

    httpretty.register_uri(
        httpretty.GET,
        re.compile("https://api.sec.or.th/FundDailyInfo/.*/dailynav/.*"),
        body=json.dumps(sec_data.multi_class_dailynav_data),
    )

    fund_name = "FUND_ID"
    remark_en = sec_data.multi_class_dailynav_data["amc_info"][0]["remark_en"]
    multi_class_nav = {k.strip(): float(v) for x in remark_en.split("/") for k, v in [x.split("=")]}
    expect_return = []
    for fund_name, nav_val in multi_class_nav.items():
        n = Nav(
            value=float(nav_val),
            updated=dateparser.parse(sec_data.multi_class_dailynav_data["nav_date"]),
            tags={},
            fund=fund_name,
        )
        n.amount = sec_data.multi_class_dailynav_data["net_asset"]
        expect_return.append(n)

    result = sec_data.sec.get_nav_from_fund_id(fund_name, sec_data.nav_date)
    assert result == expect_return


#
#   get
#
def test_get_params(sec_data):
    # date: str
    try:
        sec_data.sec.get("FUND", sec_data.nav_date.isoformat())
    except Exception:
        pytest.fail("raise exception unexpectedly")

    # Empty Fund
    with pytest.raises(ValueError):
        sec_data.sec.get("", sec_data.nav_date.isoformat())

    # date: datetime.date
    try:
        sec_data.sec.get("FUND", sec_data.nav_date)
    except Exception:
        pytest.fail("raise exception unexpectedly")

    # date: datetime.datetime
    try:
        sec_data.sec.get("FUND", datetime.datetime.combine(sec_data.nav_date, datetime.datetime.min.time()))
    except Exception:
        pytest.fail("raise exception unexpectedly")

    #
    #   get_range
    #
