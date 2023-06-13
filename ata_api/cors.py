import functools
import json
import os
from typing import Callable, Union

from fastapi import Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing_extensions import ParamSpec

from ata_api.monitoring.logging import logger
from ata_api.settings import settings


def get_cors_allowed_origins() -> list[str]:
    origins = os.environ.get("CORS_ALLOWED_ORIGINS")

    if origins is None:
        logger.warning("CORS_ALLOWED_ORIGINS not set, defaulting to empty list")
        return []

    logger.info(f"CORS_ALLOWED_ORIGINS set to {origins}")
    return json.loads(origins)  # type: ignore


P = ParamSpec("P")


def allow_cors(func: Callable[P, Union[BaseModel, Response]]) -> Callable[P, Union[BaseModel, Response]]:
    """
    Wraps a FastAPI path function to allow CORS requests.
    Works with or without the FastAPI CORS middleware.
    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Union[BaseModel, Response]:
        output = func(*args, **kwargs)

        origin = kwargs.get("origin")

        # Still check if origin is allowed in case preflight request is not sent
        if origin is None or origin not in settings.cors_allowed_origins:
            return output

        # If output is a BaseModel, return a JSONResponse with CORS headers
        if isinstance(output, BaseModel):
            return JSONResponse(
                headers={
                    "Access-Control-Allow-Origin": str(origin),
                    "Vary": "Origin",
                },
                content=output.dict(),
            )
        # If output is a Response, update its headers with CORS headers
        elif isinstance(output, Response):
            output.headers["Access-Control-Allow-Origin"] = str(origin)
            output.headers.add_vary_header("Origin")
            return output

    return wrapper
