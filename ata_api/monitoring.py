import os
from enum import auto

from aws_lambda_powertools import Metrics

from ata_api.helpers.enum import StrEnumPascal, StrEnumSnake

# Metrics
# TODO: Once we know this works, specify namespace as env variable in infra
CLOUDWATCH_METRICS_NAMESPACE = "ata-api"


class CloudWatchMetric(StrEnumPascal):
    PRESCRIPTIONS_CREATED = auto()


class CloudWatchMetricDimension(StrEnumSnake):
    SITE_NAME = auto()
    STAGE = auto()


metrics = Metrics(namespace=CLOUDWATCH_METRICS_NAMESPACE)
metrics.set_default_dimensions(**{CloudWatchMetricDimension.STAGE: os.environ.get("STAGE")})  # type: ignore
