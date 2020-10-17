from typing import Set

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Nav:
    """Class for store the NAV value with references"""

    value: float
    updated: datetime
    tags: Set[str]
    fund: str
