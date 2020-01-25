from . import sources
from .nav import Nav


def get(fund_name, source="finnomena", **kargs):
    source2class = {
        "finnomena": sources.Finnomena,
        "sec": sources.Sec,
    }
    _source = source2class[source](**kargs)

    # TODO: WIP
    raw_nav = _source.get(fund_name)
    return Nav(value=raw_nav, updated="00/00/0000", tags={"latest"}, fund=fund_name)
