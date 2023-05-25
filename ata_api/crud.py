from typing import Optional
from uuid import UUID

from ata_db_models.models import Group, UserGroup
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlmodel import select

from ata_api.helpers.decorators import raise_exception
from ata_api.helpers.enums import SiteName


@raise_exception(
    HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An exception occurred while fetching the prescription.",
    )
)
def get_prescription(session: Session, site_name: SiteName, user_id: UUID) -> Optional[UserGroup]:
    result = session.execute(
        select(UserGroup).where(UserGroup.user_id == user_id, UserGroup.site_name == site_name)
    ).one_or_none()
    return result[0] if result is not None else None


@raise_exception(
    HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An exception occurred while creating the prescription.",
    )
)
def create_prescription(session: Session, site_name: SiteName, user_id: UUID, group: Group) -> UserGroup:
    usergroup = UserGroup(
        site_name=site_name,
        user_id=user_id,
        group=group,
    )
    session.add(usergroup)
    session.commit()
    return usergroup
