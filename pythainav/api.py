from . import sources


def get(fund_name, source="finnomena", **kargs):
    fund_name = fund_name.upper()
    source2class = {
        "finnomena": sources.Finnomena,
        "sec": sources.Sec,
    }
    _source = source2class[source](**kargs)

    nav = _source.get(fund_name)
    return nav
