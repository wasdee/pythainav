import datetime
import json
import re

from unittest.mock import patch

import dateparser
import pytest
import requests

import httpretty

from pythainav.nav import Nav
from pythainav.sources import Sec


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

    test_sec = Sec(
        subscription_key={"fundfactsheet": "some_key", "funddailyinfo": "some_key"}
    )
    assert list(test_sec.subscription_key.keys()) == ["fundfactsheet", "funddailyinfo"]


#
#   search_fund
#
def test_search_fund_setting_headers(subscription_key):
    source = Sec(subscription_key=subscription_key)
    source.search_fund("FUND")

    # contain Ocp-Apim-Subscription-Key in header
    assert "Ocp-Apim-Subscription-Key" in httpretty.last_request().headers
    assert (
        httpretty.last_request().headers["Ocp-Apim-Subscription-Key"]
        == subscription_key["fundfactsheet"]
    )


def test_search_fund_invalid_key(subscription_key):
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
        httpretty.POST,
        "https://api.sec.or.th/FundFactsheet/fund",
        responses=error_responses,
    )
    source = Sec(subscription_key=subscription_key)
    with pytest.raises(requests.exceptions.HTTPError):
        source.search_fund("FUND")


def test_search_fund_success_with_content(subscription_key, dataset):
    source = Sec(subscription_key=subscription_key)
    result = source.search_fund("FUND")

    assert result == dataset["search_fund_data"]


def test_search_fund_no_content(subscription_key):
    # status code 204
    httpretty.reset()

    httpretty.register_uri(
        httpretty.POST, "https://api.sec.or.th/FundFactsheet/fund", status=204
    )

    source = Sec(subscription_key=subscription_key)
    result = source.search_fund("FUND")
    assert result is None


#
#   search_class_fund
#
def test_search_class_fund_setting_headers(subscription_key):
    source = Sec(subscription_key=subscription_key)
    source.search_class_fund("FUND")

    # contain Ocp-Apim-Subscription-Key in header
    assert "Ocp-Apim-Subscription-Key" in httpretty.last_request().headers
    assert (
        httpretty.last_request().headers["Ocp-Apim-Subscription-Key"]
        == subscription_key["fundfactsheet"]
    )


def test_search_class_fund_invalid_key(subscription_key):
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
        httpretty.POST,
        "https://api.sec.or.th/FundFactsheet/fund/class_fund",
        responses=error_responses,
    )
    source = Sec(subscription_key=subscription_key)
    with pytest.raises(requests.exceptions.HTTPError):
        source.search_class_fund("FUND")


def test_search_class_fund_success_with_content(subscription_key, dataset):
    source = Sec(subscription_key=subscription_key)
    result = source.search_class_fund("FUND")

    assert result == dataset["search_class_fund_data"]


def test_search_class_fund_no_content(subscription_key):
    # status code 204
    httpretty.reset()

    httpretty.register_uri(
        httpretty.POST,
        "https://api.sec.or.th/FundFactsheet/fund/class_fund",
        status=204,
    )

    source = Sec(subscription_key=subscription_key)
    result = source.search_class_fund("FUND")
    assert result is None


#
#   search
#
@patch("pythainav.sources.Sec.search_class_fund")
@patch("pythainav.sources.Sec.search_fund")
def test_search_result(
    mock_search_fund, mock_search_class_fund, subscription_key, dataset
):
    # search_fund found fund
    mock_search_fund.return_value = dataset["search_fund_data"]
    source = Sec(subscription_key=subscription_key)
    result = source.search("FUND")

    assert result == dataset["search_fund_data"]

    # search_fund return empty
    mock_search_fund.return_value = None
    mock_search_class_fund.return_value = dataset["search_class_fund_data"]
    result = source.search("FUND")
    assert mock_search_class_fund.called
    assert result == dataset["search_class_fund_data"]

    # both return empty
    mock_search_fund.return_value = None
    mock_search_class_fund.return_value = None
    result = source.search("FUND")
    assert result is None


#
#   list
#
def test_list_result(subscription_key, dataset):
    source = Sec(subscription_key=subscription_key)
    result = source.list()

    assert len(result) == len(dataset["search_fund_data"])


#
#   get_nav_from_fund_id
#
def test_get_nav_from_fund_id_success_with_content(subscription_key, dataset):
    # status code 200
    expect_return = Nav(
        value=float(dataset["dailynav_data"]["last_val"]),
        updated=dateparser.parse(dataset["dailynav_data"]["nav_date"]),
        tags={},
        fund="FUND_ID",
    )

    nav_date = datetime.date(2020, 1, 1)
    source = Sec(subscription_key=subscription_key)
    result = source.get_nav_from_fund_id("FUND_ID", nav_date)

    assert result == expect_return


def test_get_nav_from_fund_id_no_content(subscription_key):
    # status code 204
    httpretty.reset()

    httpretty.register_uri(
        httpretty.GET,
        re.compile("https://api.sec.or.th/FundDailyInfo/.*/dailynav/.*"),
        status=204,
    )
    nav_date = datetime.date(2020, 1, 1)
    source = Sec(subscription_key=subscription_key)
    result = source.get_nav_from_fund_id("FUND_ID", nav_date)
    assert result is None


def test_get_nav_from_fund_id_multi_class(subscription_key, dataset):
    httpretty.reset()

    httpretty.register_uri(
        httpretty.GET,
        re.compile("https://api.sec.or.th/FundDailyInfo/.*/dailynav/.*"),
        body=json.dumps(dataset["multi_class_dailynav_data"]),
    )

    fund_name = "FUND_ID"
    remark_en = dataset["multi_class_dailynav_data"]["amc_info"][0]["remark_en"]
    multi_class_nav = {
        k.strip(): float(v) for x in remark_en.split("/") for k, v in [x.split("=")]
    }
    expect_return = []
    for fund_name, nav_val in multi_class_nav.items():
        n = Nav(
            value=float(nav_val),
            updated=dateparser.parse(dataset["multi_class_dailynav_data"]["nav_date"]),
            tags={},
            fund=fund_name,
        )
        n.amount = dataset["multi_class_dailynav_data"]["net_asset"]
        expect_return.append(n)

    nav_date = datetime.date(2020, 1, 1)
    source = Sec(subscription_key=subscription_key)
    result = source.get_nav_from_fund_id(fund_name, nav_date)
    assert result == expect_return


#
#   get
#
def test_get_params(subscription_key):
    nav_date = datetime.date(2020, 1, 1)
    source = Sec(subscription_key=subscription_key)

    # date: str
    try:
        source.get("FUND", nav_date.isoformat())
    except Exception:
        pytest.fail("raise exception unexpectedly")

    # Empty Fund
    with pytest.raises(ValueError):
        source.get("", nav_date.isoformat())

    # date: datetime.date
    try:
        source.get("FUND", nav_date)
    except Exception:
        pytest.fail("raise exception unexpectedly")

    # date: datetime.datetime
    try:
        source.get(
            "FUND", datetime.datetime.combine(nav_date, datetime.datetime.min.time())
        )
    except Exception:
        pytest.fail("raise exception unexpectedly")
