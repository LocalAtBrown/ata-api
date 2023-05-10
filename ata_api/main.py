from typing import Generator
from uuid import UUID

from ata_db_models.helpers import get_conn_string
from ata_db_models.models import Group, UserGroup
from fastapi import Depends, FastAPI, HTTPException, status
from mangum import Mangum
from pydantic import BaseModel
from sqlalchemy.orm import Session, sessionmaker
from sqlmodel import create_engine, select

from ata_api.helpers.enums import SiteName
from ata_api.helpers.logging import logging

logger = logging.getLogger(__name__)

app = FastAPI()
engine = create_engine(url=get_conn_string())
session_factory = sessionmaker(autoflush=False, autocommit=False, bind=engine)


def create_db_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency that opens and closes a DB session.
    (See: https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/.)
    """
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


class PrescriptionResponse(BaseModel):
    site_name: SiteName
    user_id: UUID
    group: Group


@app.get("/")
def get_root() -> object:
    return {"message": "This is the root endpoint for the AtA API."}


@app.get("/prescription/{site_name}/{user_id}", response_model=PrescriptionResponse)
def get_or_create_prescription(
    site_name: str, user_id: str, session: Session = Depends(create_db_session)
) -> PrescriptionResponse:
    # Verify if user_id is a valid UUID string of 32 hexadecimal digits
    try:
        user_id_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid user ID: {user_id}")

    # test if site exists
    if site_name not in {*SiteName}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid site: {site_name}")

    # query db for user/site group
    try:
        query_results = session.execute(
            select(UserGroup).where(UserGroup.user_id == user_id_uuid, UserGroup.site_name == site_name)
        ).first()
    except Exception as e:
        logger.exception(f"Site: {site_name}, user ID: {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="There was a problem with the database"
        )

    # if no row for the user/site, create it, else grab the first row since session.execute().first() still returns a list
    if query_results is None:
        try:
            usergroup = UserGroup(user_id=user_id_uuid, site_name=site_name)
            session.add(usergroup)
            session.commit()
        except Exception as e:
            logger.exception(f"Site: {site_name}, user ID: {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="There was a problem with the database"
            )
    else:
        usergroup = query_results[0]

    return PrescriptionResponse(site_name=usergroup.site_name, user_id=usergroup.user_id, group=usergroup.group)


handler = Mangum(app)
