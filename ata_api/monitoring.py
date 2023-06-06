import os
from enum import auto

from aws_lambda_powertools import Metrics

from ata_api.helpers.enum import StrEnumPascal, StrEnumSnake


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
