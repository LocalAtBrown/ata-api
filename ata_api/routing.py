# adapted from https://www.eliasbrange.dev/posts/observability-with-fastapi-aws-lambda-powertools/
from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import Request, Response
from fastapi.routing import APIRoute

from ata_api.monitoring.logging import logger


class LoggerRouteHandler(APIRoute):
    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        original_route_handler = super().get_route_handler()

        async def route_handler(request: Request) -> Response:
            # Add fastapi context to logs
            context = {
                "path": request.url.path,
                "route": self.path,
                "method": request.method,
            }
            logger.append_keys(fastapi=context)  # type: ignore
            logger.info("Received request")

            return await original_route_handler(request)

        return route_handler
