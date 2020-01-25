from . import sources


def get(fund_name, source="finnomena", **kargs):
    """
    Gets the latest NAV

    **Parameters:**

    * **fund_name** - Fund name found in finnomena such as `TISTECH-A`
    * **source** - *(optional)* Data source for pull data. See Data Sources
    section in the documentation for all availiable options.
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

    nav = _source.get(fund_name)
    return nav
