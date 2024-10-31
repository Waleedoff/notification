import json
import re
from datetime import date, datetime, time

from sqlalchemy import Column, DateTime, String, inspect
from sqlalchemy.event import listen
from sqlalchemy.future.engine import create_engine
from sqlalchemy.orm import Mapped, declarative_base, declared_attr, sessionmaker
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.pool import StaticPool

from app.common.enums import LoggingLevel
from app.common.utils import generate_random_uuid
from app.config import BaseConfig
from sqlalchemy_utils.listeners import instant_defaults_listener

DELETE_DATETIME = datetime.fromtimestamp(0)


def datetime_encoder(val):
    if isinstance(val, date):
        return val.isoformat()

    if isinstance(val, time):
        return val.isoformat()

    raise TypeError()


Base = declarative_base()


class BaseDb(object):
    def __init__(self, config: BaseConfig):
        engine_options = {
            "echo": "debug" if config.ENVIRONMENT == "staging" else False,
            "echo_pool": "debug" if config.LOGGING_LEVEL == LoggingLevel.DEBUG else False,
            "poolclass": StaticPool,  # no pooling from sqlalchemy
            "future": True,
            "json_serializer": lambda obj: json.dumps(obj, default=datetime_encoder),
        }

        if config.SQL_POOL_ENABLED:
            engine_options.update(
                {
                    "pool_size": config.SQL_POOL_SIZE,
                    "max_overflow": config.SQL_POOL_OVERFLOW_SIZE,
                }
            )
            del engine_options["poolclass"]

        self.engine = create_engine(config.SQLALCHEMY_DATABASE_URL, **engine_options)  # type: ignore[arg-type, call-overload]
        self.read_engine = create_engine(config.SQLALCHEMY_READ_DATABASE_URL, **engine_options)  # type: ignore[arg-type, call-overload]

        # following https://fastapi.tiangolo.com/tutorial/sql-databases
        sessionmaker_optins = {
            "autocommit": False,
            "autoflush": False,
            "expire_on_commit": False,
            "future": True,
        }

        self.SessionLocal = sessionmaker(bind=self.engine, **sessionmaker_optins)  # type: ignore[arg-type, call-overload]
        self.ReadSessionLocal = sessionmaker(bind=self.read_engine, **sessionmaker_optins)  # type: ignore[arg-type, call-overload]

        listen(Defaults, "init", instant_defaults_listener, propagate=True)


class Defaults:
    """
    this DbBase should be used for all of our models it dose:
    1. add created and updated using code from sqlalchemy_utils.Timestamp
    2. Generate __tablename__ automatically User -> users
    3. ids (id) a random uuid
    4. created_by
    """

    __override_tablename__: str | None = None

    @declared_attr
    def __tablename__(cls):
        if cls.__override_tablename__ is not None:
            return cls.__override_tablename__
        return re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower() + "s"  # type: ignore[attr-defined]

    id: Mapped[str] = Column(String, primary_key=True, default=generate_random_uuid)  # type: ignore

    created_by: Mapped[str] = Column(String, nullable=False, index=True)  # type: ignore
    created: Mapped[datetime] = Column(DateTime, default=datetime.now, nullable=False)  # type: ignore
    updated: Mapped[datetime] = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)  # type: ignore

    def update_attributes(self, new_data: dict):
        # NOTE columns_to_deleted key used to set any key value to None
        columns_to_deleted = new_data.pop("columns_to_deleted", [])

        for key, value in new_data.items():
            if value is not None:
                if value == DELETE_DATETIME or key in columns_to_deleted:
                    value = None
                self.__setattr__(key, value)
                is_from_attributesl = isinstance(value, Base)
                is_list_of_from_attributesl = isinstance(value, list) and len(value) > 0 and isinstance(value[0], Base)
                is_a_primry_key = value == inspect(self).mapper.primary_key_from_instance(self)[0]  # type: ignore
                if not is_from_attributesl and not is_list_of_from_attributesl and not is_a_primry_key:
                    flag_modified(self, key)  # force to update this attrebute

        return self

listen(Defaults, "init", instant_defaults_listener, propagate=True)
