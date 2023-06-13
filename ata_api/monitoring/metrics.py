import functools
from collections.abc import Callable
from enum import auto
from typing import TypeVar, Union

from aws_lambda_powertools import Metrics, single_metric
from aws_lambda_powertools.metrics import MetricUnit
from typing_extensions import ParamSpec

from ata_api.helpers.enum import StrEnumPascal, StrEnumSnake
from ata_api.monitoring.logging import logger
from ata_api.settings import settings

P = ParamSpec("P")
R = TypeVar("R")


class CloudWatchMetric(StrEnumPascal):
    PRESCRIPTIONS_CREATED = auto()
    PRESCRIPTIONS_READ = auto()


class CloudWatchMetricDimension(StrEnumSnake):
    GROUP = auto()
    SITE_NAME = auto()
    STAGE = auto()


# Namespace is defined as an env var in the ata-infrastucture repo
metrics = Metrics()

if settings.stage is not None:
    metrics.set_default_dimensions(**{CloudWatchMetricDimension.STAGE: settings.stage})  # type: ignore


def log_cloudwatch_metric(
    name: str,
    value: float,
    unit: MetricUnit,
    dimensions: dict[str, Union[str, Callable[[R], str]]],
    log_if_output_is_none: bool = False,
    default_dimensions: dict[str, str] = metrics.default_dimensions,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Wraps a function to log a CloudWatch metric.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # First, call the function
            output = func(*args, **kwargs)

            # If func returns None and we don't want to log any metric in this case,
            # we're good to go
            if output is None and not log_if_output_is_none:
                return output

            # Log the metric
            try:
                with single_metric(name=name, unit=unit, value=value, default_dimensions=default_dimensions) as metric:
                    for dimension_name, dimension_value in dimensions.items():
                        # If the dimension value is a constant, use it as-is
                        if isinstance(dimension_value, str):
                            metric.add_dimension(name=dimension_name, value=dimension_value)
                        # If the dimension value is a function, it needs to be called with the output of the func.
                        else:
                            metric.add_dimension(name=dimension_name, value=dimension_value(output))
            except Exception:
                logger.exception("Failed to log metric")
            finally:
                return output

        return wrapper

    return decorator
