from fastapi import Depends
from sqlalchemy.orm import Session

from app.common.redis_client import get_redis_client
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


get_db_session = get_db_session_dependency(db.SessionLocal)
db_session = Depends(get_db_session)

