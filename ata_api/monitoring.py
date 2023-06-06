import functools
import os
from collections.abc import Callable
from enum import auto
from typing import TypeVar

from aws_lambda_powertools import Metrics, single_metric
from aws_lambda_powertools.metrics import MetricUnit
from typing_extensions import ParamSpec

from ata_api.helpers.enum import StrEnumPascal, StrEnumSnake
from ata_api.helpers.logging import logging

logger = logging.getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


# ---------- METRICS ----------
class CloudWatchMetric(StrEnumPascal):
    PRESCRIPTIONS_CREATED = auto()


class CloudWatchMetricDimension(StrEnumSnake):
    SITE_NAME = auto()
    STAGE = auto()


# Namespace is defined as an env var in the ata-infrastucture repo
metrics = Metrics()

if os.environ.get("STAGE") is not None:
    metrics.set_default_dimensions(**{CloudWatchMetricDimension.STAGE: os.environ["STAGE"]})  # type: ignore


def log_cloudwatch_metric(
    name: str,
    value: float,
    dimensions: dict[str, str],
    unit: MetricUnit = MetricUnit.Count,
    default_dimensions: dict[str, str] = metrics.default_dimensions,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Wraps a function to log a CloudWatch metric.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                with single_metric(name=name, unit=unit, value=value, default_dimensions=default_dimensions) as metric:
                    for dimension_name, dimension_value in dimensions.items():
                        metric.add_dimension(name=dimension_name, value=dimension_value)
            except Exception as e:
                logger.exception(f"Failed to log metric: {e}")
            finally:
                return func(*args, **kwargs)

        return wrapper

    return decorator
