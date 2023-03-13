from ata_db_models.helpers import get_conn_string
from ata_db_models.models import Prescription
from fastapi import FastAPI
from mangum import Mangum
from sqlmodel import Session, create_engine, select

app = FastAPI()
engine = create_engine(url=get_conn_string())


@app.get("/")
def get_root():
    return {"message": "This is the root endpoint for the AtA API."}


@app.get("/prescription/{site_name}/{user_id}", response_model=list[Prescription])
def read_prescription(site_name: str, user_id: str):
    with Session(engine) as session:
        prescription = session.exec(
            select(Prescription).where(Prescription.user_id == user_id, Prescription.site_name == site_name)
        ).first()
        return prescription


handler = Mangum(app)
