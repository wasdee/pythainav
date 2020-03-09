from typing import List

from . import sources
from .nav import Nav
from .utils._optional import import_optional_dependency


def get(fund_name, *, source="finnomena", date=None, **kargs) -> Nav:
    """
    Gets the latest NAV

    **Parameters:**

    * **fund_name** - Fund name found in finnomena such as `TISTECH-A`
    * **source** - *(optional)* Data source for pull data. See Data Sources
    section in the documentation for all availiable options.
    * **date** - *(optional)* get latest price of a given date
    * **subscription_key** - *(optional)* Subscription key that required for
    a data source like `sec` (a.k.a)

    **Returns:** `Nav`

    Usage:
    ```
    >>> import pythainav as nav

    >>> nav.get("KT-PRECIOUS")
    Nav(value=4.2696, updated='20/01/2020', tags={'latest'}, fund='KT-PRECIOUS')
    ```
    """
    fund_name = fund_name.upper()

    source2class = {
        "finnomena": sources.Finnomena,
        "sec": sources.Sec,
    }
    _source = source2class[source](**kargs)

    nav = _source.get(fund_name, date)

    return nav


def get_all(fund_name, *, source="finnomena", asDataFrame=False, **kargs) -> List[Nav]:
    """
    Gets the latest NAV

    **Parameters:**

    * **fund_name** - Fund name found in finnomena such as `TISTECH-A`
    * **source** - *(optional)* Data source for pull data. See Data Sources
    section in the documentation for all availiable options.
    * **asDataFrame** - *(optional)* return pandas dataframe instead.
    * **subscription_key** - *(optional)* Subscription key that required for
    a data source like `sec` (a.k.a)


    **Returns:** `List[Nav]` or `pd.DataFrame`

    Usage:
    ```
    >>> import pythainav as nav

    >>> nav.get_all("KT-PRECIOUS")
    [Nav(value=4.2696, updated='20/01/2020', tags={'latest'}, fund='KT-PRECIOUS'), ...]

    >>> nav.get_all("KT-PRECIOUS", asDataFrame=True)
    ```
    """
    fund_name = fund_name.upper()

    source2class = {
        "finnomena": sources.Finnomena,
        "sec": sources.Sec,
    }
    _source = source2class[source](**kargs)

    navs = _source.get_range(fund_name)

    if asDataFrame:
        pd = import_optional_dependency("pandas")
        from dataclasses import asdict

        navs = pd.DataFrame([asdict(x) for x in navs])

    return navs
