import functools
from typing import Callable, Union

from fastapi import Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing_extensions import ParamSpec

from ata_api.settings import settings

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
                content=jsonable_encoder(output),
            )
        # If output is a Response, update its headers with CORS headers
        elif isinstance(output, Response):
            output.headers["Access-Control-Allow-Origin"] = str(origin)
            output.headers.add_vary_header("Origin")
            return output

    return wrapper
