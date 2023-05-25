import random
from typing import Annotated, Generator
from uuid import UUID

from ata_db_models.helpers import get_conn_string
from ata_db_models.models import Group
from fastapi import Depends, FastAPI, Path, Query
from mangum import Mangum
from pydantic import BaseModel
from sqlalchemy.orm import Session, sessionmaker
from sqlmodel import create_engine

from ata_api.crud import create_prescription, get_prescription
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
    site_name: Annotated[SiteName, Path(title="Site name")],
    user_id: Annotated[UUID, Path(title="Snowplow user ID")],
    wa: Annotated[int, Query(title="Weight of assignment to A", ge=0)] = 1,
    wb: Annotated[int, Query(title="Weight of assignment to B", ge=0)] = 1,
    wc: Annotated[int, Query(title="Weight of assignment to C", ge=0)] = 1,
    session: Session = Depends(create_db_session),
) -> PrescriptionResponse:
    # TODO: This would be a good place to perform a canary-style ramp-up. After ascertaining that the user
    # is in indeed new, we could assign them to a group with a low probability of being selected for the
    # intervention, i.e., the code below. This probability could be increased over time.
    usergroup = get_prescription(session, site_name, user_id) or create_prescription(
        session, site_name, user_id, group=random.choices([Group.A, Group.B, Group.C], weights=[wa, wb, wc], k=1)[0]
    )

    return PrescriptionResponse(site_name=usergroup.site_name, user_id=usergroup.user_id, group=usergroup.group)


handler = Mangum(app)
