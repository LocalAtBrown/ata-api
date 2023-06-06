import os
import random
from typing import Annotated
from uuid import UUID

from ata_db_models.models import Group
from aws_lambda_powertools.metrics import MetricUnit, single_metric
from fastapi import Depends, FastAPI, Path, Query
from mangum import Mangum
from sqlalchemy.orm import Session

from ata_api.crud import create_prescription, get_prescription
from ata_api.db import create_db_session
from ata_api.helpers.logging import logging
from ata_api.models import PrescriptionResponse
from ata_api.monitoring import (
    CLOUDWATCH_METRICS_NAMESPACE,
    CloudWatchMetric,
    CloudWatchMetricDimension,
    metrics,
)
from ata_api.site import SiteName

logger = logging.getLogger(__name__)

app = FastAPI()

logger.info(f"AtA API starting up on stage {os.environ.get('STAGE')}")


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
    # Get group assignment
    usergroup = get_prescription(session, site_name, user_id)

    # If not exists, create a new group assignment
    if usergroup is None:
        usergroup = create_prescription(
            session, site_name, user_id, group=random.choices([Group.A, Group.B, Group.C], weights=[wa, wb, wc], k=1)[0]
        )
        # Log metric
        if os.environ.get("STAGE") is not None:
            try:
                with single_metric(
                    name=CloudWatchMetric.PRESCRIPTIONS_CREATED,
                    unit=MetricUnit.Count,
                    value=1,
                    namespace=CLOUDWATCH_METRICS_NAMESPACE,
                ) as metric:
                    metric.add_dimension(name=CloudWatchMetricDimension.STAGE, value=os.environ.get("STAGE"))  # type: ignore
                    metric.add_dimension(name=CloudWatchMetricDimension.SITE_NAME, value=site_name)
            except Exception as e:
                logger.exception(f"Failed to log metric: {e}")

    return PrescriptionResponse(site_name=usergroup.site_name, user_id=usergroup.user_id, group=usergroup.group)


handler = Mangum(app)

# Add metrics last to properly flush metrics
handler = metrics.log_metrics(handler, capture_cold_start_metric=True)
