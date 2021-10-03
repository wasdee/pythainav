import pytest
import pythainav as nav


def test_get_nav():
    kt_nav = nav.get("KT-PRECIOUS")
    print(kt_nav)
    assert kt_nav.value >= 0


def test_get_nav_with_date():
    oil_nav = nav.get("TMBOIL", date="1 week ago")
    print(oil_nav)
    assert oil_nav.value >= 0


def test_get_all():
    kt_navs = nav.get_all("KT-PRECIOUS")
    print(kt_navs)
    assert len(kt_navs) >= 0


def test_get_all_pandas():
    import pandas as pd

    df = nav.get_all("KT-PRECIOUS", asDataFrame=True)
    assert isinstance(df, pd.DataFrame)


@pytest.mark.skip(reason="For dev only, required real api key")
def test_sec_source():
    from decouple import config

    subs_key = {
        "fundfactsheet": config("FUND_FACTSHEET_KEY"),
        "funddailyinfo": config("FUND_DAILY_INFO_KEY"),
    }

    # should auto convert to friday if it is a weekend
    # kt_nav = nav.get("KT-PRECIOUS", source="sec", subscription_key=subs_key)
    # print(kt_nav)
    # assert kt_nav.value >= 0

    kt_nav = nav.get(
        "KT-PRECIOUS",
        source="sec",
        subscription_key=subs_key,
        date="03/04/2020",
    )
    print(kt_nav)
    assert kt_nav.value >= 0
