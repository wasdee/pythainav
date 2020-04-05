import re
import json
from tests.factories.search_fund import SearchFundFactory
from tests.factories.search_class_fund import SearchClassFundFactory
from tests.factories.dailynav import DailyNavFactory, AMCInfoFactory


def setup_sec_data(unit_test, httpretty):
    httpretty.reset()
    if not httpretty.is_enabled():
        httpretty.enable()

    unit_test.search_fund_data = SearchFundFactory.build_batch(5)
    unit_test.search_class_fund_data = SearchClassFundFactory.build_batch(5)
    unit_test.dailynav_data = DailyNavFactory.create()

    multi_class_dailynav_data = DailyNavFactory.create(class_fund=True)
    multi_class_amc_info = AMCInfoFactory(class_fund=True)
    multi_class_dailynav_data["amc_info"] = [multi_class_amc_info]
    unit_test.multi_class_dailynav_data = multi_class_dailynav_data

    # FundFactsheet 3
    httpretty.register_uri(
        httpretty.POST, "https://api.sec.or.th/FundFactsheet/fund", body=json.dumps(unit_test.search_fund_data)
    )

    # FundFactsheet 21
    httpretty.register_uri(
        httpretty.POST,
        "https://api.sec.or.th/FundFactsheet/fund/class_fund",
        body=json.dumps(unit_test.search_class_fund_data),
    )

    # FundDailyInfo 1
    httpretty.register_uri(
        httpretty.GET,
        re.compile("https://api.sec.or.th/FundDailyInfo/.*/dailynav/.*"),
        body=json.dumps(unit_test.dailynav_data),
    )
