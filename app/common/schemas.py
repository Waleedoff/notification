from typing import Callable

from fastapi import HTTPException,  Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute

from app.common.logging import logger


class ValidationErrorLoggingRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                return await original_route_handler(request)
            except RequestValidationError as exc:
                body = await request.body()
                detail = {"errors": exc.errors(), "body": body.decode()}
                logger.exception(detail)
                raise HTTPException(status_code=422, detail=detail)

        return custom_route_handler

