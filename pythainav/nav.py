from dataclasses import dataclass
from datetime import datetime
from typing import Set


@dataclass
class Nav(object):
    """Class for store the NAV value with references"""

    value: float
    updated: datetime
    tags: Set[str]
    fund: str
