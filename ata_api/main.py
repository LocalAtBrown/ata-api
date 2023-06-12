import os
import random
from typing import Annotated
from uuid import UUID

from ata_db_models.models import Group
from fastapi import Depends, Path, Query
from mangum import Mangum
from sqlalchemy.orm import Session

from ata_api.app import app
from ata_api.crud import create_prescription, read_prescription
from ata_api.db import create_db_session
from ata_api.models import PrescriptionResponse
from ata_api.monitoring.logging import logger
from ata_api.monitoring.metrics import metrics
from ata_api.site import SiteName

logger.info(f"AtA API starting up on stage {os.environ.get('STAGE')}")


@app.get("/")
def get_root() -> object:
    return {"message": "This is the root endpoint for the AtA API."}


@app.get("/prescription/{site_name}/{user_id}", response_model=PrescriptionResponse)
def get_prescription(
    site_name: Annotated[SiteName, Path(title="Site name")],
    user_id: Annotated[UUID, Path(title="Snowplow user ID")],
    wa: Annotated[int, Query(title="Weight of assignment to A", ge=0)] = 1,
    wb: Annotated[int, Query(title="Weight of assignment to B", ge=0)] = 1,
    wc: Annotated[int, Query(title="Weight of assignment to C", ge=0)] = 1,
    session: Session = Depends(create_db_session),
) -> PrescriptionResponse:
    # Get group assignment. If it doesn't exist, create it.
    logger.info(f"Reading prescription for user {user_id} at site {site_name}")
    usergroup = read_prescription(session, site_name, user_id)

    if usergroup is None:
        logger.info(f"Prescription not found. Creating prescription for user {user_id} at site {site_name}")
        usergroup = create_prescription(
            session, site_name, user_id, group=random.choices([Group.A, Group.B, Group.C], weights=[wa, wb, wc], k=1)[0]
        )

    return PrescriptionResponse(site_name=usergroup.site_name, user_id=usergroup.user_id, group=usergroup.group)


handler = Mangum(app)

# Add logging
handler = logger.inject_lambda_context(handler, clear_state=True)
# Add metrics last to properly flush metrics
handler = metrics.log_metrics(handler, capture_cold_start_metric=True)
