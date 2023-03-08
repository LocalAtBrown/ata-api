from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()


@app.get("/")
def get_root():
    return {"message": "FastAPI running in a Lambda function"}


handler = Mangum(app)
