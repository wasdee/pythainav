import factory


class AMCInfoFactory(factory.Factory):
    class Meta:
        model = dict

    class Params:
        class_fund = factory.Trait(
            sell_price=0.0,
            buy_price=0.0,
            sell_swap_price=0.0,
            buy_swap_price=0.0,
            remark_th="กองทุน A= 10.3393/กองทุน D= 10.3516/กองทุน R= 10.3055",
            remark_en="Fund-A= 10.3393/Fund-D= 10.3516/Fund-R= 10.3055",
        )

    unique_id = factory.Sequence(lambda n: 'C{:0>10}'.format(n))
    sell_price = 10.9585
    buy_price = 10.7226
    sell_swap_price = 10.9585
    buy_swap_price = 10.7226
    remark_th = " "
    remark_en = " "


class DailyNavFactory(factory.Factory):

    class Meta:
        model = dict

    class Params:
        class_fund = factory.Trait(
            last_val=0.0,
            previous_val=0.00,
            # amc_info = factory.List([factory.SubFactory(AMCInfoFactory, factory.SelfAttribute("..class_fund"))])
        )

    last_upd_date = "2020-01-01T01:02:03"
    nav_date = "2020-01-01"
    net_asset = 1234567890
    last_val = 10.7226
    previous_val = 10.5931
    amc_info = factory.List([factory.SubFactory(AMCInfoFactory)])
