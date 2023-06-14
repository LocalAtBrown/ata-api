from functools import lru_cache
from typing import Optional

from ata_db_models.helpers import Stage
from pydantic import BaseSettings, HttpUrl

from ata_api.monitoring.logging import logger


class Settings(BaseSettings):
    """
    Settings for the AtA API, including but not limited to those set with
    environment variables.
    """

    # If you want to use an environment variable, add it here.
    stage: Optional[Stage] = None
    cors_allowed_origins: set[HttpUrl] = set()


@lru_cache
def get_settings(log: bool = False) -> Settings:
    settings = Settings()

    if log is True:
        if len(settings.cors_allowed_origins) == 0:
            logger.warning("CORS_ALLOWED_ORIGINS not set, defaulting to empty list")
        else:
            logger.info(f"CORS_ALLOWED_ORIGINS set to {settings.cors_allowed_origins}")

    return settings


settings = get_settings(log=True)
