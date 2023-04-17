from os import getenv
from random import randint

from ata_db_models.helpers import get_conn_string
from ata_db_models.models import Prescription
from fastapi import FastAPI
from mangum import Mangum
from sqlmodel import Session, create_engine, select

app = FastAPI()
engine = create_engine(url=get_conn_string())
STRATEGY = getenv("STRATEGY", "RCT")


@app.get("/")
def get_root() -> object:
    return {"message": "This is the root endpoint for the AtA API."}


@app.get("/prescription/{site_name}/{user_id}", response_model=int)
def read_prescription(site_name: str, user_id: str) -> int:
    if STRATEGY == "RCT":
        return fair_coin_toss()
    else:
        return get_prescription_from_db(site_name=site_name, user_id=user_id)


def fair_coin_toss() -> int:
    return randint(0, 1)


def ignore_existing_subscribers() -> bool:
    # todo
    ...


def get_prescription_from_db(site_name: str, user_id: str) -> int:
    with Session(engine) as session:
        prescription = session.exec(
            select(Prescription).where(Prescription.user_id == user_id, Prescription.site_name == site_name)
        ).first()
        if prescription:
            return int(prescription.prescribe)
        return 0


handler = Mangum(app)
