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


def set_unloaded_relationship_to_none(cls, value):
    if isinstance(value, dict):
        return value

    def _set_unloaded_relationship_to_none(*, object):
        inspect_data = inspect(object)
        return {**inspect_data.dict, **{key: None for key in inspect_data.unloaded}}

    if isinstance(value._obj, list):
        return [_set_unloaded_relationship_to_none(object=object) for object in value._obj]

    else:
        return _set_unloaded_relationship_to_none(object=value._obj)


def extract_user_data(*, user, **kwargs):
    return dict(
        email=user.email,
        data=dict(name=user.name, username=user.username, **kwargs),
    )


def get_download_url(key: str, bucket_name: str):
    if key.startswith("http"):
        logger.debug(f"get_download_url got key starting with http!! , key:{key}, bucket:{bucket_name}")
        return key
    return f"https://{bucket_name}/{key}"


def get_asset_key(asset_id, file_type):
    return f"{file_type}/{asset_id}"


def url_to_string(url: HttpUrl | None) -> str | None:
    if url is None:
        return url

    return str(url)


def get_query_count(query, session) -> int:
    """
    this will change the query to make it faster and return the count
    from
    ### Slow: SELECT COUNT(*) FROM (SELECT ... FROM TestModel WHERE ...) ...
    to
    ### Fast: SELECT COUNT(*) FROM model WHERE ...
    :param query:
    :return count:int
    """
    count_q = select(func.count()).select_from(query.subquery())
    count = session.execute(count_q)
    return count.scalar()


# def get_column_name_by_lang(*, obj, lang: LanguageLocale, col_name_prefix: str) -> str:
#     return getattr(obj, f"{col_name_prefix}_{lang.value.lower()}")


# def generate_qr(qr_data: str) -> MIMEImage:
#     buffer = BytesIO()
#     img = qrcode.make(qr_data)
#     img.save(buffer, "PNG")

#     image = MIMEImage(buffer.getvalue())
#     image.add_header("Content-ID", "<qrcode>")
#     image.add_header("Content-Disposition", "attachment", filename="qr_code.png")

#     return image


def clean_for_csv(value: str):
    value = str(value)
    if '"' in value:
        value = value.replace('"', "'")

    if 'None' in value:
        value = value.replace('None', " ")

    return f'"{value}"'


def get_csv_response_from_list_of_dict(dict_list: list[dict], file_name: str):
    key_value_list = []

    dict_keys = [clean_for_csv(key) for key in dict_list[0].keys()]
    for dictionary in dict_list:
        dict_values = [clean_for_csv(value) for value in dictionary.values()]
        key_value_list.append(",".join(dict_values) + "\n")
    key_value_list.insert(0, ",".join(dict_keys) + "\n")

    filename = f"{file_name}.csv"
    response = StreamingResponse(content=iter(key_value_list), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response


def batch(iterable, limit: int):
    length = len(iterable)
    for ndx in range(0, length, limit):
        yield iterable[ndx : min(ndx + limit, length)]
