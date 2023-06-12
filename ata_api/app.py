from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.exceptions import ExceptionMiddleware

from ata_api.monitoring.logging import logger
from ata_api.routing import LoggerRouteHandler

app = FastAPI()
# Add FastAPI context to logs
app.router.route_class = LoggerRouteHandler
# Add exception middleware to log unhandled exceptions
app.add_middleware(ExceptionMiddleware, handlers=app.exception_handlers)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exception: Exception) -> JSONResponse:
    logger.exception("Unhandled exception")
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal Server Error"})
