from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Nav(object):
    """Class for store the NAV value with references"""

    value: float
    updated: datetime
    tags: List[str]
    fund: str
