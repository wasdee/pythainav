import factory
import six
import random


def get_fund_status():
    choices = ["RG", "EX", "SE", "CA", "LI"]
    return random.choices(choices, weights=[93, 1, 4, 1, 1], k=1).pop()


def get_invest_country_flag():
    choices = ["1", "2", "3", "4"]
    return random.choice(choices)


class SearchFundFactory(factory.Factory):
    class Meta:
        model = dict

    proj_id = factory.Sequence(lambda n: "M{:0>4}_25{:0>2}".format(n, n))
    regis_id = factory.Sequence(lambda n: "{:0>3}_25{:0>2}".format(n, n) if n % 5 == 0 else "-")
    regis_date = factory.Sequence(lambda n: "2020-01-{:0>2}".format(n + 1) if n % 5 == 0 else "-")
    cancel_date = factory.Sequence(lambda n: "2020-01-{:0>2}".format(n + 1) if n % 5 == 0 else "-")
    proj_name_th = factory.Sequence(lambda n: "กองทุน {}".format(n))
    proj_name_en = factory.Sequence(lambda n: "Fund {}".format(n))
    proj_abbr_name = factory.Sequence(lambda n: "FUND-{:0>2}".format(n))
    funds_status = factory.LazyFunction(get_fund_status)
    unique_id = factory.Sequence(lambda n: "C{:0>10}".format(n))
    permit_us_investment = "-"
    invest_country_flag = factory.LazyFunction(get_invest_country_flag)
    last_upd_date = "2020-01-01T01:02:03"
