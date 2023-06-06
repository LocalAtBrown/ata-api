from enum import Enum
from typing import Any

from caseconverter import kebabcase, pascalcase, snakecase


class StrEnum(str, Enum):
    """
    StrEnum class. Replace with built-in version after upgrading to Python 3.10.
    """

    def __str__(self) -> str:
        return f"{self.value}"


# There's probably a metaclass way to make these cleaner
class StrEnumKebab(StrEnum):
    """
    StrEnum class where the value is kebab-case.
    """

    @staticmethod
    def _generate_next_value_(name: str, *args: Any, **kwargs: Any) -> str:
        return kebabcase(name)  # type: ignore


class StrEnumPascal(StrEnum):
    """
    StrEnum class where the value is PascalCase.
    """

    @staticmethod
    def _generate_next_value_(name: str, *args: Any, **kwargs: Any) -> str:
        return pascalcase(name)  # type: ignore


class StrEnumSnake(StrEnum):
    """
    StrEnum class where the value is snake_case.
    """

    @staticmethod
    def _generate_next_value_(name: str, *args: Any, **kwargs: Any) -> str:
        return snakecase(name)  # type: ignore
