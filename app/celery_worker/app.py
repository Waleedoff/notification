import os
import time
from functools import wraps

from celery import Celery
from celery.app.task import Task
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.session import SessionTransaction

from app.common.logging import logging
from app.common.redis_client import RedisClient, get_redis_client
from app.config import BaseConfig
from app.db.db import BaseDb
# from app.dependencies import get_feature_flags_dependency


def stop_http_errors(func):
    @wraps(func)
    def new_func(*args, **kwargs):

        try:
            return func(*args, **kwargs)
        except HTTPException as e:
            raise Exception(f"HTTPException: code: {e.status_code}, detail: {e.detail}")

    return new_func


class CustomTask(Task):
    app_config: BaseConfig
    session: Session
    read_only_session: Session
    feature_flags: dict
    redis_client: RedisClient
    transaction: SessionTransaction


def init_app(config: BaseConfig):
    # setting timezone
    os.environ["TZ"] = config.APP_TZ
    time.tzset()

    base_db = BaseDb(config)

    backend = config.CELERY_RESULT_BACKEND
    if backend is None:
        backend = config.CELERY_BROKER_URL

    client = Celery(
        config.APP_NAME,
        backend=backend if config.CELERY_ENABLE_RESULT_BACKEND else None,
        borker=config.CELERY_BROKER_URL,
    )
    # get_feature_flags = get_feature_flags_dependency(config, base_db)

    class FullCustomTask(CustomTask):
        _session: Session | None = None
        _read_only_session: Session | None = None
        _redis_client: RedisClient | None = None
        transaction: SessionTransaction

        def before_start(self, *args, **kwargs):
            if config.testing:
                raise Exception("THIS IS NOT TEST TASK")

        def after_return(self, *args, **kwargs):
            if self._session is not None:
                self._session.commit()
                self._session.close()
                self._session = None
            if self._read_only_session is not None:
                self._read_only_session.close()
                self._read_only_session = None

        @property
        def app_config(self):
            return config

        @property
        def feature_flags(self):
            return get_feature_flags()

        @property
        def session(self):
            if self._session is None:
                self._session = base_db.SessionLocal()
                self.transaction = self._session.begin()
            return self._session

        @property
        def read_only_session(self):
            if self._read_only_session is None:
                self._read_only_session = base_db.ReadSessionLocal()
            return self._read_only_session

        @property
        def redis_client(self):
            if self._redis_client is None:
                self._redis_client = get_redis_client(config)
            return self._redis_client

        priority = 9
        if not config.testing:
            autoretry_for = (Exception,) if config.ENABLE_CELERY_RETRY else tuple()
            retry_backoff = True if config.ENABLE_CELERY_RETRY_BACKOFF else False
            max_retries = config.CELERY_RETRY_MAX
            retry_backoff_max = config.CELERY_RETRY_BACKOFF_MAX

        def on_failure(self, exc, task_id, args, kwargs, einfo):
            if isinstance(exc, HTTPException):
                exc = Exception(f"HTTPException: code: {exc.status_code}, detail: {exc.detail}")
            logging.exception(exc, exc_info=True)
            if self._session is not None:
                self._session.close()
                self._session = None
            super().on_failure(exc, task_id, args, kwargs, einfo)

        def on_retry(self, exc, task_id, args, kwargs, einfo):
            if self._session is not None:
                self._session.close()
                self._session = None
            if self._read_only_session is not None:
                self._read_only_session.close()
                self._read_only_session = None
            return super().on_retry(exc, task_id, args, kwargs, einfo)

    client.Task = FullCustomTask
    client.conf["task_always_eager"] = config.testing
    if not config.testing:
        pass
        # from app.common.set_up_sentry import set_up_sentry
        # set_up_sentry(config)

    return client
