from os import getenv
from uuid import UUID

from ata_db_models.helpers import get_conn_string
from ata_db_models.models import Group, Prescription, UserGroup
from fastapi import FastAPI
from mangum import Mangum
from sqlmodel import Session, create_engine, select

app = FastAPI()
engine = create_engine(url=get_conn_string())
POLICY = getenv("POLICY", "RCT")


@app.get("/")
def get_root() -> object:
    return {"message": "This is the root endpoint for the AtA API."}


@app.get("/prescription/{site_name}/{user_id}", response_model=int)
def read_prescription(site_name: str, user_id: str) -> int:
    # if no row for the user/site, create it
    # based on the group, return the prescription
    # A: original (so... 1?)
    # B: run scroll depth calc
    # C: no show (0)
    with Session(engine) as session:
        # query db for user/site group
        usergroup = session.exec(
            select(UserGroup).where(UserGroup.user_id == user_id, UserGroup.site_name == site_name)
        ).first()
        # if no row for the user/site, create it (so if usergroup is none/empty
        if not usergroup:
            usergroup = UserGroup(user_id=UUID(user_id), site_name=site_name)
            session.add(usergroup)
            session.commit()
        # TODO insert user_id + site_name, with RETURNING statement for group
        if usergroup.group == Group.A:
            # show existing CTA
            return 1
        elif usergroup.group == Group.B:
            # model
            # TODO
            # if not enough data to do this, return default
            return -1
        elif usergroup.group == Group.C:
            # no show
            return 0
        else:
            # shouldn't get here, safe default of 0
            return 0


def get_prescription_from_db(site_name: str, user_id: str) -> int:
    with Session(engine) as session:
        prescription = session.exec(
            select(Prescription).where(Prescription.user_id == user_id, Prescription.site_name == site_name)
        ).first()
        if prescription:
            return int(prescription.prescribe)
        return 0


handler = Mangum(app)
