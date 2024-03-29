import random
from typing import Annotated, Any, Union
from uuid import UUID

import lambdawarmer
from ata_db_models.models import Group
from fastapi import Depends, Header, Path, Query, Response
from mangum import Mangum
from mangum.types import LambdaContext
from pydantic import HttpUrl
from sqlalchemy.orm import Session

from ata_api.app import app
from ata_api.cors import evaluate_cors
from ata_api.crud import create_prescription, read_prescription
from ata_api.db import create_db_session
from ata_api.models import PrescriptionResponse
from ata_api.monitoring.logging import logger
from ata_api.monitoring.metrics import metrics
from ata_api.settings import Settings, get_settings
from ata_api.site import SiteName

AnnotatedOrigin = Annotated[Union[HttpUrl, None], Header(title="Origin of request")]
AnnotatedSettings = Annotated[Settings, Depends(get_settings)]


@app.get("/")
def get_root(
    response: Response,
    settings: AnnotatedSettings,
    origin: AnnotatedOrigin = None,
) -> dict[str, str]:
    # Evaluate CORS
    evaluate_cors(response, origin, settings.cors_allowed_origins)

    return {"message": "This is the root endpoint for the AtA API."}


@app.get("/prescription/{site_name}/{user_id}", response_model=PrescriptionResponse)
def get_prescription(
    response: Response,
    settings: AnnotatedSettings,
    session: Annotated[Session, Depends(create_db_session)],
    site_name: Annotated[SiteName, Path(title="Site name")],
    user_id: Annotated[UUID, Path(title="Snowplow user ID")],
    wa: Annotated[int, Query(title="Weight of assignment to A", ge=0)] = 1,
    wb: Annotated[int, Query(title="Weight of assignment to B", ge=0)] = 1,
    wc: Annotated[int, Query(title="Weight of assignment to C", ge=0)] = 1,
    origin: AnnotatedOrigin = None,
) -> PrescriptionResponse:
    # Get group assignment. If it doesn't exist, create it.
    logger.info(f"Reading prescription for user {user_id} at site {site_name}")
    usergroup = read_prescription(session, site_name, user_id)

    if usergroup is None:
        logger.info(f"Prescription not found. Creating prescription for user {user_id} at site {site_name}")
        usergroup = create_prescription(
            session, site_name, user_id, group=random.choices([Group.A, Group.B, Group.C], weights=[wa, wb, wc], k=1)[0]
        )

    # Evaluate CORS
    evaluate_cors(response, origin, settings.cors_allowed_origins)

    return PrescriptionResponse(site_name=usergroup.site_name, user_id=usergroup.user_id, group=usergroup.group)


@metrics.log_metrics(capture_cold_start_metric=True)  # type: ignore  # Add metrics last to properly flush metrics
@logger.inject_lambda_context(clear_state=True)  # Add logging
@lambdawarmer.warmer  # type: ignore  # Keep the lambda warm (in addition, need to set up CloudWatch event to ping every 5 minutes)
def handler(event: dict[str, Any], context: LambdaContext) -> dict[str, Any]:
    asgi_handler = Mangum(app)
    return asgi_handler(event, context)
