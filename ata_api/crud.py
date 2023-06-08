from typing import Optional
from uuid import UUID

from ata_db_models.models import Group, UserGroup
from aws_lambda_powertools.metrics import MetricUnit
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlmodel import select

from ata_api.helpers.functools import raise_exception
from ata_api.monitoring.metrics import (
    CloudWatchMetric,
    CloudWatchMetricDimension,
    log_cloudwatch_metric,
)
from ata_api.site import SiteName


def get_usergroup_site_name(usergroup: UserGroup) -> SiteName:
    return usergroup.site_name  # type: ignore # until TODO we make a SiteName enum in ata-db-models


def get_usergroup_group(usergroup: UserGroup) -> Group:
    return usergroup.group


@log_cloudwatch_metric(
    name=CloudWatchMetric.PRESCRIPTIONS_READ,
    value=1,
    unit=MetricUnit.Count,
    dimensions={
        CloudWatchMetricDimension.SITE_NAME: get_usergroup_site_name,
        CloudWatchMetricDimension.GROUP: get_usergroup_group,
    },
)
@raise_exception(
    HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An exception occurred while fetching the prescription.",
    )
)
def read_prescription(session: Session, site_name: SiteName, user_id: UUID) -> Optional[UserGroup]:
    """
    Returns the prescription for the given user_id and site_name, or None if it doesn't exist.
    The read metric is logged only if the prescription exists.
    """
    result = session.execute(
        select(UserGroup).where(UserGroup.user_id == user_id, UserGroup.site_name == site_name)
    ).one_or_none()
    return result[0] if result is not None else None


@log_cloudwatch_metric(
    name=CloudWatchMetric.PRESCRIPTIONS_CREATED,
    value=1,
    unit=MetricUnit.Count,
    dimensions={
        CloudWatchMetricDimension.SITE_NAME: get_usergroup_site_name,
        CloudWatchMetricDimension.GROUP: get_usergroup_group,
    },
)
@raise_exception(
    HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An exception occurred while creating the prescription.",
    )
)
def create_prescription(session: Session, site_name: SiteName, user_id: UUID, group: Group) -> UserGroup:
    """
    Creates a prescription for the given user_id and site_name.
    """
    usergroup = UserGroup(
        site_name=site_name,
        user_id=user_id,
        group=group,
    )
    session.add(usergroup)
    session.commit()
    return usergroup
