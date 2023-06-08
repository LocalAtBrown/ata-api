import functools
from collections.abc import Callable
from typing import TypeVar

from typing_extensions import ParamSpec

from ata_api.monitoring.logging import logger

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
                logger.exception(
                    f"An exception occurred in while calling function {func.__name__} "
                    + f"with args {args} and kwargs {kwargs}: {exception_internal}"
                )
                raise exception

        return wrapper

    return decorator
