from uuid import UUID

from ata_db_models.models import Group
from pydantic import BaseModel

from ata_api.helpers.enums import SiteName


class PrescriptionResponse(BaseModel):
    site_name: SiteName
    user_id: UUID
    group: Group
