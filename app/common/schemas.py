import re
from datetime import date, datetime
from typing import Callable, Optional, is_typeddict

from fastapi import HTTPException, Query, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from pydantic import BaseModel, EmailStr, Field

from app.common.logging import logger

pagenation_response_names = []


class RolesInfo(BaseModel):
    id: str
    name: str


class RolesRequest(BaseModel):
    roles: list[RolesInfo]

    class Config:
        from_attributes = True


class PagenationQueryParams:
    def __init__(
        self, offset: int = Query(0, ge=0), limit: int = Query(20, le=100, gt=0)
    ):
        self.offset = offset
        self.limit = limit


def PagenationResponse(Schema, extra_key=""):
    global pagenation_response_names

    class PagenationResponse(BaseModel):
        max_count: int | None = None
        total_count: int | None = None
        result_list: list[Schema]

    if is_typeddict(Schema):
        schema_name = "PagenationResponse" + extra_key
    else:
        schema_name = "PagenationResponse" + Schema.__name__ + extra_key
    if schema_name in pagenation_response_names:
        # this is a check to avoid duplecated names witch breaks the docs
        raise Exception(
            f"this name is duplecated, please change the extra_key from '{extra_key}'"
        )

    pagenation_response_names.append(schema_name)
    PagenationResponse.__name__ = schema_name
    return PagenationResponse


class IsOpenResponse(BaseModel):
    is_open: bool


class ToggleApplicationsRequest(BaseModel):
    ids: list[str] = Field(min_length=1)


# https://fastapi.tiangolo.com/how-to/custom-request-and-route/#accessing-the-request-body-in-an-exception-handler
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


def validate_datetime_greater_than_current(start_at: datetime):
    current_time = datetime.now()
    if start_at <= current_time:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"start_at must be greater than current time current_time: {current_time}, start_at: {start_at}",
        )
    return start_at


def validate_end_at_with_start_at(end_at: datetime, start_at: Optional[datetime]):
    current_time = datetime.now()
    if end_at <= current_time:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"end_at must be greater than current time: {end_at}, current_time: {current_time}",
        )

    if start_at is not None and start_at >= end_at:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"end_at must be greater than start_at, start_at: {start_at}, end_at: {end_at}",
        )

    return end_at


def validate_string_without_number(v: str, k: str):
    if any(char.isdigit() for char in v):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{k} must not contain numbers",
        )
    return v


def validate_number_without_string(v: str):
    if not re.fullmatch(r"\d+", v):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Mobile number must contain only digits",
        )
    return v


def validate_password(v: str):
    value = v.strip()
    pattern = re.compile(
        r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    )
    if pattern.match(value) is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="password should be 8 characters and combination of capital and small letters and special characters",
        )
    return value


def check_dates_greater_than_current(cls, v: date):
    if v <= date.today():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Dates must be greater than the current date",
        )
    return v


def check_end_at_after_start_at(cls, v: date, values):
    start_at = values.get("start_at")
    if start_at and v <= start_at:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="End date must be greater than start date",
        )
    return v


def validate_date(start_at: date):
    current_date = date.today()
    if start_at < current_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"start_at must be greater than current date. current_date: {current_date}, start_at: {start_at}",
        )
    return start_at


def validate_start_with_end_date(end_at: date, start_at: date):
    current_date = date.today()
    if end_at < current_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"end_at must be greater than current date. end_at: {end_at}, current_date: {current_date}",
        )
    if start_at > end_at:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"end_at must be greater than start_at. start_at: {start_at}, end_at: {end_at}",
        )
    return end_at


class CreateKeycloakUserRequest(BaseModel):
    username: str
    email: EmailStr
    enabled: bool
    credentials: list[dict]
    requiredActions: list[str]
