from typing import Optional

from ata_db_models.helpers import Stage
from pydantic import BaseSettings, HttpUrl

from ata_api.monitoring.logging import logger


class Settings(BaseSettings):
    stage: Optional[Stage] = None
    cors_allowed_origins: set[HttpUrl] = set()


settings = Settings()
if len(settings.cors_allowed_origins) == 0:
    logger.warning("CORS_ALLOWED_ORIGINS not set, defaulting to empty list")
else:
    logger.info(f"CORS_ALLOWED_ORIGINS set to {settings.cors_allowed_origins}")
