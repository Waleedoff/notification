from threading import Lock
from typing import Callable

from cachetools import TTLCache, cached
from cachetools.keys import hashkey
from fastapi import Depends
from sqlalchemy import column, table
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select

from app.common.auth_service import AuthService
from app.common.enums import BaseEnum
from app.common.keycloak_api import KeycloakAdminApiService
from app.common.redis_client import get_redis_client
from app.common.schemas import PagenationQueryParams
from app.db.db import BaseDb

from .config import BaseConfig, config

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


def get_redis_dependency(config: BaseConfig):
    def _get_redis_client():
        return get_redis_client(config)

    return _get_redis_client


def get_keycloak_api_service():
    return KeycloakAdminApiService()


def get_feature_flags_dependency(config: BaseConfig, db: BaseDb):
    local_cash: TTLCache = TTLCache(
        maxsize=config.FEATURE_FLAG_LOCAL_CASH_SIZE_LIMIT,
        ttl=config.FEATURE_FLAG_LOCAL_CACHING_TTL,
    )
    lock = Lock()

    def _get_feature_flags():
        # don't use this directly!
        session: Session = db.SessionLocal()
        results = session.execute(
            select(
                table(
                    "feature_flags",
                    column("key"),
                    column("value"),
                )
            )
        )
        feature_flags = results.all()
        session.close()
        return {key: value for key, value in feature_flags}

    @cached(cache=local_cash, key=hashkey, lock=lock)
    def get_cached_feature_flags():
        return _get_feature_flags()

    return get_cached_feature_flags



def get_auth_service(config: BaseConfig):
    return AuthService(
        server_url=config.KEYCLOAK_SERVER_URL,
        client_id=config.KEYCLOAK_CLIENT_ID,
        realm_name=config.KEYCLOAK_REALM,
        redis_host=config.REDIS_HOST,
        redis_port=config.REDIS_PORT,
        redis_db=config.REDIS_DB,
        config=config,
    )


def permissions_required(*permissions: BaseEnum):
    def permissions_required_dependance(
        login_required=Depends(
            _auth_service.login_required(
                [*[permission.value for permission in permissions]]
            )
        ),
    ):
        pass

    return Depends(permissions_required_dependance)


_auth_service = get_auth_service(config)
get_db_session = get_db_session_dependency(db.SessionLocal)
db_session = Depends(get_db_session)
get_db_read_session = get_db_session_dependency(db.ReadSessionLocal)
db_read_session = Depends(get_db_read_session)
keycloak_admin_api = Depends(get_keycloak_api_service)
current_user = Depends(_auth_service.current_user())
pagination_params = Depends(PagenationQueryParams)

redis_client = Depends(get_redis_dependency(config=config))

feature_flags = Depends(get_feature_flags_dependency(config, db))

pagination_params = Depends(PagenationQueryParams)
