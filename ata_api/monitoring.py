from aws_lambda_powertools import Metrics

from ata_api.helpers.enum import StrEnumPascal
from enum import auto

# Metrics
metrics = Metrics(namespace="ata-api")  # TODO: Specify namespace as env variable in infra


class CloudWatchMetric(StrEnumPascal):
    PRESCRIPTIONS_CREATED = auto()