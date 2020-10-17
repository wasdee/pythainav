import datetime
import json
import re

from unittest.mock import patch

import dateparser
import pytest

import httpretty

from pythainav.nav import Nav
from pythainav.sources import Onde


#
#   search_fund
#
def test_search_fund_success_with_content(dataset):
    source = Onde()
    result = source.search_fund("FUND")

    assert result == dataset["search_fund_data"]


def test_search_fund_no_content():
    # status code 204
    httpretty.reset()

    httpretty.register_uri(
        httpretty.POST,
        "http://dataexchange.onde.go.th/api/ApiProxy/Data/3C154331-4622-406E-94FB-443199D35523/f2529128-0332-44a0-9066-034093b07837/fund",
        status=204,
    )

    source = Onde()
    result = source.search_fund("FUND")
    assert result is None


#
#   search_class_fund
#
def test_search_class_fund_success_with_content(dataset):
    source = Onde()
    result = source.search_class_fund("FUND")

    assert result == dataset["search_class_fund_data"]


def test_search_class_fund_no_content():
    # status code 204
    httpretty.reset()

    httpretty.register_uri(
        httpretty.POST,
        "http://dataexchange.onde.go.th/api/ApiProxy/Data/3C154331-4622-406E-94FB-443199D35523/f2529128-0332-44a0-9066-034093b07837/fund/class_fund",
        status=204,
    )

    source = Onde()
    result = source.search_class_fund("FUND")
    assert result is None


#
#   search
#
@patch("pythainav.sources.Onde.search_class_fund")
@patch("pythainav.sources.Onde.search_fund")
def test_search_result(mock_search_fund, mock_search_class_fund, dataset):
    # search_fund found fund
    mock_search_fund.return_value = dataset["search_fund_data"]
    source = Onde()
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
def test_list_result(dataset):
    source = Onde()
    result = source.list()

    assert len(result) == len(dataset["search_fund_data"])


#
#   get_nav_from_fund_id
#
def test_get_nav_from_fund_id_success_with_content(dataset):
    # status code 200
    expect_return = Nav(
        value=float(dataset["dailynav_data"]["last_val"]),
        updated=dateparser.parse(dataset["dailynav_data"]["nav_date"]),
        tags={},
        fund="FUND_ID",
    )

    nav_date = datetime.date(2020, 1, 1)
    source = Onde()
    result = source.get_nav_from_fund_id("FUND_ID", nav_date)

    assert result == expect_return


def test_get_nav_from_fund_id_no_content():
    # status code 204
    httpretty.reset()

    httpretty.register_uri(
        httpretty.GET,
        re.compile(
            "http://dataexchange.onde.go.th/api/ApiProxy/Data/92b67f7e-023e-4ce8-b4ba-08989d44ff78/ed6867e7-2d97-49e3-b25b-8bb0edb18e1c/.*/dailynav/.*"
        ),
        status=204,
    )
    nav_date = datetime.date(2020, 1, 1)
    source = Onde()
    result = source.get_nav_from_fund_id("FUND_ID", nav_date)
    assert result is None


def test_get_nav_from_fund_id_multi_class(dataset):
    httpretty.reset()

    httpretty.register_uri(
        httpretty.GET,
        re.compile(
            "http://dataexchange.onde.go.th/api/ApiProxy/Data/92b67f7e-023e-4ce8-b4ba-08989d44ff78/ed6867e7-2d97-49e3-b25b-8bb0edb18e1c/.*/dailynav/.*"
        ),
        body=json.dumps(dataset["multi_class_dailynav_data"]),
    )

    fund_name = "FUND_ID"
    remark_en = dataset["multi_class_dailynav_data"]["amc_info"][0]["remark_en"]
    multi_class_nav = {k.strip(): float(v) for x in remark_en.split("/") for k, v in [x.split("=")]}
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
    source = Onde()
    result = source.get_nav_from_fund_id(fund_name, nav_date)
    assert result == expect_return


#
#   get
#
def test_get_params():
    nav_date = datetime.date(2020, 1, 1)
    source = Onde()

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
        source.get("FUND", datetime.datetime.combine(nav_date, datetime.datetime.min.time()))
    except Exception:
        pytest.fail("raise exception unexpectedly")
