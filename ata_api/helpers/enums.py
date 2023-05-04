from enum import Enum, auto
from typing import Any


class StrEnum(str, Enum):
    """
    StrEnum class. Replace with built-in version after upgrading to Python 3.10.
    """

    @staticmethod
    def _generate_next_value_(name: str, *args: Any, **kwargs: Any) -> str:
        return name.lower().replace("_", "-")

    def __str__(self) -> str:
        return f"{self.value}"


class SiteName(StrEnum):
    THE_19TH = auto()
    OPEN_VALLEJO = auto()
    DALLAS_FREE_PRESS = auto()
    AFRO_LA = auto()
