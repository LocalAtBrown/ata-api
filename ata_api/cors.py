from typing import Optional

from fastapi import Response
from pydantic import HttpUrl


def evaluate_cors(response: Response, origin: Optional[HttpUrl], cors_allowed_origins: set[HttpUrl]) -> None:
    """
    Evaluates the origin of a request and updates the response headers accordingly.
    """
    if origin is not None and origin in cors_allowed_origins:
        response.headers.update(
            {
                "Access-Control-Allow-Origin": str(origin),
                "Vary": "Origin",
            }
        )
