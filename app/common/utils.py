from email.mime.image import MIMEImage
from io import BytesIO
from uuid import uuid4

# import qrcode
from fastapi.responses import StreamingResponse
from pydantic import HttpUrl
from sqlalchemy import func, inspect, select

# from app.common.enums import LanguageLocale
from app.common.logging import logger


def generate_random_uuid():
    return str(uuid4())


def remove_none_params(param: dict):
    new_params = dict()
    for key, value in param.items():
        if value is not None:
            new_params[key] = value
    return new_params


def url_to_string(url: HttpUrl | None) -> str | None:
    if url is None:
        return url

    return str(url)


def chunk_list(lst: list[str], chunk_size: int) -> list[list[str]]:
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def batch(iterable, limit: int):
    length = len(iterable)
    for ndx in range(0, length, limit):
        yield iterable[ndx : min(ndx + limit, length)]
