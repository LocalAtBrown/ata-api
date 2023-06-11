import json
import os

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import ExceptionMiddleware

from ata_api.monitoring.logging import logger
from ata_api.routing import LoggerRouteHandler


def get_cors_allowed_origins() -> list[str]:
    origins = os.environ.get("CORS_ALLOWED_ORIGINS")

    if origins is None:
        logger.warning("CORS_ALLOWED_ORIGINS not set, defaulting to empty list")
        return []

    logger.info(f"CORS_ALLOWED_ORIGINS set to {origins}")
    return json.loads(origins)  # type: ignore


app = FastAPI()
# Add FastAPI context to logs
app.router.route_class = LoggerRouteHandler
# Add CORS whitelist
app.add_middleware(CORSMiddleware, allow_origins=get_cors_allowed_origins(), allow_methods=["GET"])
# Add exception middleware to log unhandled exceptions
app.add_middleware(ExceptionMiddleware, handlers=app.exception_handlers)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exception: Exception) -> JSONResponse:
    logger.exception("Unhandled exception")
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal Server Error"})
