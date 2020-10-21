import json
import re

import pytest

from furl import furl

import httpretty

# from tests.factories.dailynav import AMCInfoFactory
# from tests.factories.dailynav import DailyNavFactory
# from tests.factories.search_class_fund import SearchClassFundFactory
# from tests.factories.search_fund import SearchFundFactory


@pytest.fixture
def subscription_key():
    subscription_key = {"fundfactsheet": "fact_key", "funddailyinfo": "daily_key"}
    return subscription_key


# @pytest.fixture
# def dataset():
#     dataset = {}
#     dataset["search_fund_data"] = SearchFundFactory.build_batch(5)
#     dataset["search_class_fund_data"] = SearchClassFundFactory.build_batch(5)
#     dataset["dailynav_data"] = DailyNavFactory.create()
#
#     multi_class_dailynav_data = DailyNavFactory.create(class_fund=True)
#     multi_class_amc_info = AMCInfoFactory(class_fund=True)
#     multi_class_dailynav_data["amc_info"] = [multi_class_amc_info]
#     dataset["multi_class_dailynav_data"] = multi_class_dailynav_data
#     return dataset


@pytest.fixture(autouse=True)
def set_global_test_data(request):
    httpretty.reset()
    if not httpretty.is_enabled():
        httpretty.enable()

    dataset = request.getfixturevalue("dataset")

    #
    # Sec
    #
    # FundFactsheet 3
    httpretty.register_uri(
        httpretty.POST,
        "https://api.sec.or.th/FundFactsheet/fund",
        body=json.dumps(dataset["search_fund_data"]),
    )

    # FundFactsheet 21
    httpretty.register_uri(
        httpretty.POST,
        "https://api.sec.or.th/FundFactsheet/fund/class_fund",
        body=json.dumps(dataset["search_class_fund_data"]),
    )

    # FundDailyInfo 1
    httpretty.register_uri(
        httpretty.GET,
        re.compile("https://api.sec.or.th/FundDailyInfo/.*/dailynav/.*"),
        body=json.dumps(dataset["dailynav_data"]),
    )

    #
    # Onde
    #
    base_url = {
        "fundfactsheet": furl(
            "http://dataexchange.onde.go.th/api/ApiProxy/Data/3C154331-4622-406E-94FB-443199D35523/f2529128-0332-44a0-9066-034093b07837/fund"
        )
    }
    # FundFactsheet 3
    httpretty.register_uri(
        httpretty.POST,
        base_url["fundfactsheet"].url,
        body=json.dumps(dataset["search_fund_data"]),
    )

    # FundFactsheet 21
    httpretty.register_uri(
        httpretty.POST,
        base_url["fundfactsheet"].copy().add(path=["class_fund"]).url,
        body=json.dumps(dataset["search_class_fund_data"]),
    )

    # FundDailyInfo 1
    httpretty.register_uri(
        httpretty.GET,
        re.compile(
            "http://dataexchange.onde.go.th/api/ApiProxy/Data/92b67f7e-023e-4ce8-b4ba-08989d44ff78/ed6867e7-2d97-49e3-b25b-8bb0edb18e1c/.*/dailynav/.*"
        ),
        body=json.dumps(dataset["dailynav_data"]),
    )
    yield
    httpretty.disable()
