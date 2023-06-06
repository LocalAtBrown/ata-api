import functools
from collections.abc import Callable
from typing import TypeVar

from typing_extensions import ParamSpec

from ata_api.helpers.logging import logging

logger = logging.getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


def raise_exception(exception: Exception) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Accepts an Exception as an argument and wraps around a function.
    When the function short-circuits, the exception is raised.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return func(*args, **kwargs)
            except Exception as exception_internal:
                logger.exception(f"{args}, {kwargs}: {exception_internal}")
                raise exception

        return wrapper

    return decorator
