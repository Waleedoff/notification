
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.db import BaseDb

from .config import config

db = BaseDb(config)



def get_db_session_dependency(SessionLocal):
    def get_db_session():
        session: Session = SessionLocal()
        try:
            with session.begin():
                yield session
        finally:
            session.close()

    return get_db_session


# TODO we don't need this anymore cause we use the jwt with fastapi.security.OAuth2PasswordBearer

# def get_auth_service(config: BaseConfig):
#     return AuthService(
#         server_url=config.KEYCLOAK_SERVER_URL,
#         client_id=config.KEYCLOAK_CLIENT_ID,
#         realm_name=config.KEYCLOAK_REALM,
#         redis_host=config.REDIS_HOST,
#         redis_port=config.REDIS_PORT,
#         redis_db=config.REDIS_DB,
#         config=config,
#     )


# def get_feature_flags_dependency(config: BaseConfig, db: BaseDb):
#     local_cash: TTLCache = TTLCache(
#         maxsize=config.FEATURE_FLAG_LOCAL_CASH_SIZE_LIMIT, ttl=config.FEATURE_FLAG_LOCAL_CACHING_TTL
#     )
#     lock = Lock()

#     def _get_feature_flags():
#         # don't use this dirctly!
#         session: Session = db.SessionLocal()
#         results = session.execute(
#             select(
#                 table(
#                     "feature_flags",
#                     column("key"),
#                     column("value"),
#                 )
#             )
#         )
#         feature_flags = results.all()
#         session.close()
#         return {key: value for key, value in feature_flags}

#     @cached(cache=local_cash, key=hashkey, lock=lock)
#     def get_cached_feature_flags():
#         return _get_feature_flags()

#     return get_cached_feature_flags



# TODO CHECK IT HOW TO USE IT WITH FASTAPI..

# _auth_service = get_auth_service(config)
# current_user = Depends(_auth_service.current_user())
# login_required = Depends(_auth_service.login_required())


get_db_session = get_db_session_dependency(db.SessionLocal)
db_session = Depends(get_db_session)

get_db_read_session = get_db_session_dependency(db.ReadSessionLocal)
db_read_session = Depends(get_db_read_session)

# get_feature_flags = get_feature_flags_dependency(config, db)
# feature_flags = Depends(get_feature_flags)



# TODO check if you want recaptcha or not??

# def get_recaptcha_dependency() -> Callable:
#     def _get_recaptcha(request: Request, recaptcha_token: str = Header(...)) -> None:
#         import requests

#         from app.common.exceptions import InvalidGoogleRecaptcha

#         if config.ENVIRONMENT not in ["staging", "prod"]:
#             return

#         if recaptcha_token is None:
#             raise InvalidGoogleRecaptcha

#         if config.RECAPTCHA_SECRET_V3 is None:
#             raise Exception("no RECAPTCHA_SECRET_V3 in envs!")

#         assert request.client is not None
#         params = {
#             "secret": config.RECAPTCHA_SECRET_V3,
#             "response": recaptcha_token,
#             "remoteip": request.client.host,
#         }
#         response = requests.post(url=config.GOOGLE_RECAPTCHA_URL_CHECK, params=params)

#         result: dict = response.json()
#         is_success = result.get("success", False)

#         if not is_success:
#             raise InvalidGoogleRecaptcha

#     return _get_recaptcha


# recaptcha_v3_required = Depends(get_recaptcha_dependency())


# TODO CHECK ON THE PERMISSIONS_REQUIRED SETUP WITH FASTAPI

# def permissions_required(*permissions: BaseEnum):
#     def permissions_required_dependance(
#         login_required=Depends(_auth_service.login_required([*[permission.value for permission in permissions]])),
#     ):
#         pass

#     return Depends(permissions_required_dependance)
