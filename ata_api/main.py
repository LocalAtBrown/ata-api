from uuid import UUID

from ata_db_models.helpers import get_conn_string
from ata_db_models.models import Group, UserGroup
from fastapi import FastAPI, HTTPException
from mangum import Mangum
from pydantic import BaseModel
from sqlmodel import Session, create_engine, select, text

from ata_api.helpers.enums import SiteName
from ata_api.helpers.logging import logging

logger = logging.getLogger(__name__)

app = FastAPI()
engine = create_engine(url=get_conn_string())


class PrescriptionResponse(BaseModel):
    group: Group
    value: int


@app.get("/")
def get_root() -> object:
    return {"message": "This is the root endpoint for the AtA API."}


@app.get("/prescription/{site_name}/{user_id}", response_model=PrescriptionResponse)
def get_prescription(site_name: str, user_id: str) -> PrescriptionResponse:
    # Verify if user_id is a valid UUID string of 32 hexadecimal digits
    try:
        user_id_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Invalid user ID: {user_id}")

    # test if site exists
    if site_name not in [*SiteName]:
        raise HTTPException(status_code=404, detail=f"Invalid site: {site_name}")

    with Session(engine) as session:
        # query db for user/site group
        try:
            usergroup = session.exec(
                select(UserGroup).where(UserGroup.user_id == user_id_uuid, UserGroup.site_name == site_name)
            ).first()
        except Exception as e:
            logger.exception(f"Site: {site_name}, user ID: {user_id}: {e}")
            raise HTTPException(status_code=404, detail="There was a problem with the database")

        # if no row for the user/site, create it
        if not usergroup:
            try:
                usergroup = UserGroup(user_id=user_id_uuid, site_name=site_name)
                session.add(usergroup)
                session.commit()
            except Exception as e:
                logger.exception(f"Site: {site_name}, user ID: {user_id}: {e}")
                raise HTTPException(status_code=404, detail="There was a problem with the database")

        if usergroup.group == Group.A:
            # show CTA
            return PrescriptionResponse(group=Group.A, value=1)
        elif usergroup.group == Group.B:
            # model
            # TODO: delete this if decide to use plugin to calculate scroll depth
            statement = text(
                f"""
            WITH prep AS (SELECT LEAST(
                                 LEAST(
                                         GREATEST(
                                                 MAX(coalesce(ev.pp_yoffset_max, 0)),
                                                 0),
                                         MAX(ev.doc_height)
                                     ) + MAX(ev.br_viewheight),
                                 MAX(ev.doc_height)
                         ) / MAX(ev.doc_height)::FLOAT
                         as relative_vmax
                          FROM event AS ev
                          WHERE ev.doc_height > 0
                            AND ev.domain_userid = '{user_id_uuid}'
                            AND ev.site_name = '{site_name}'
                          GROUP BY domain_sessionidx, page_urlpath)
            SELECT avg(relative_vmax) AS avg_relative_vmax
            FROM prep;
            """
            )
            scroll_depth = session.execute(statement).first()

            try:
                # change this 0.3 for a different scroll depth threshold
                if scroll_depth[0] > 0.3:  # type: ignore
                    return PrescriptionResponse(group=Group.B, value=1)
                else:
                    return PrescriptionResponse(group=Group.B, value=0)
            except TypeError:
                # not enough data to calculate, return a default
                return PrescriptionResponse(group=Group.B, value=0)
        elif usergroup.group == Group.C:
            # no show
            return PrescriptionResponse(group=Group.C, value=0)
        else:
            # shouldn't get here, safe default of 0
            return PrescriptionResponse(group=Group.C, value=0)


handler = Mangum(app)
