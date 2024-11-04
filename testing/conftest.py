import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import column, insert, select, table
from sqlalchemy.orm import Session, scoped_session
from app.api.users.models import User
from app.celery_worker.tasks import celery

from sqlalchemy_utils import create_database, drop_database
from app.common.enums import UserGroup
from app.common.permissions import Permission
from app.common.utils import generate_token
from app.config import config
from app.db.db import BaseDb
from app.dependencies import (
    feature_flags,
    get_db_read_session,
    get_db_session,
    get_feature_flags_dependency,
    get_keycloak_api_service,
)
from app.main import app
from testing.helpers import get_seed_data
from testing.keycloak_api_override import get_test_keycloak_api_service

base_db = BaseDb(config)
ScopedSession = scoped_session(base_db.SessionLocal, scopefunc=lambda: "")


# ======================================= TEST SETUP ======================================= #


def get_feature_flags_overwrite():
    session = ScopedSession()
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
    return {key: value for key, value in feature_flags}


def get_celery_test_task():
    class TestCustomTask(celery.Task):
        _session = None
        _read_only_session = None
        _external_services = None
        _feature_flags = None
        _redis_client = None

        def before_start(self, *args, **kwargs):
            ScopedSession().flush()
            self._session = None
            self._read_only_session = None

        def after_return(self, *args, **kwargs):
            if self._session is not None:
                self._session.flush()
                # we can't expire_all here ,, because it will delete extra properties such as user in any object >_<
                # self._session.expire_all()

        @property
        def app_config(self):
            return config

        @property
        def session(self):
            if self._session is None:
                self._session = ScopedSession()

            return self._session

    task = TestCustomTask
    return task


def get_db_session_overwrite():
    test_session = ScopedSession()
    test_session.expire_all()
    temp_session = test_session.begin_nested()

    try:
        yield test_session
        if temp_session.is_active:
            temp_session.commit()
    except Exception as e:
        import logging

        if temp_session.is_active:
            temp_session.rollback()
        logging.exception(e, exc_info=True)
        raise


@pytest.fixture
def vc_jobSeeker_headers():
    user = next(
        user
        for user in get_seed_data()["users"]
        if user["role"] == UserGroup.VC_JOBSEEKER.value
    )

    return dict(
        Authorization=generate_token(
            data=dict(
                sub=user["id"],
                email_verified=True,
                realm_access=dict(roles=[Permission.SiteAccess.VC_JOBSEEKER]),
            )
        ),
        Content_Type="application/json",
    )


@pytest.fixture
def vc_admin_headers():
    user = next(
        user
        for user in get_seed_data()["users"]
        if user["role"] == UserGroup.VC_ADMIN.value
    )

    return dict(
        Authorization=generate_token(
            data=dict(
                sub=user["id"],
                email_verified=True,
                realm_access=dict(roles=[Permission.SiteAccess.VC_ADMIN]),
            )
        ),
        Content_Type="application/json",
    )
    
@pytest.fixture
def vc_company_headers():
    user = next(
        user
        for user in get_seed_data()["users"]
        if user["role"] == UserGroup.VC_COMPANY.value
    )

    return dict(
        Authorization=generate_token(
            data=dict(
                sub=user["id"],
                email_verified=True,
                realm_access=dict(roles=[Permission.SiteAccess.VC_COMPANY]),
            )
        ),
        Content_Type="application/json",
    )


@pytest.fixture(autouse=True)
def transaction_flag():
    db_connection = base_db.engine.connect()
    db_connection.begin()
    ScopedSession(bind=db_connection)
    yield
    # so next time we create a session from ScopedSession
    # a new session will be created instead of using the same session
    ScopedSession.remove()
    db_connection.close()


@pytest.fixture(autouse=True, scope="session")
def seed_data(client):
    db_connection = base_db.engine.connect()
    ScopedSession.remove()

    with db_connection.begin():
        session: Session = ScopedSession(bind=db_connection)
        users = get_seed_data()["users"]
        for user in users:
            user.pop("role", None)
        session.execute(insert(User).values(users))

    ScopedSession.remove()
    db_connection.close()


@pytest.fixture()
def session():
    return ScopedSession()


@pytest.fixture(scope="session")
def client() -> TestClient:  # type: ignore
    """
    Create a Postgres database for the tests, and drop it when the tests are done.
    """

    app.dependency_overrides[get_db_session] = get_db_session_overwrite
    app.dependency_overrides[get_db_read_session] = get_db_session_overwrite
    app.dependency_overrides[feature_flags] = get_feature_flags_dependency
    app.dependency_overrides[get_keycloak_api_service] = get_test_keycloak_api_service

    try:
        create_database(base_db.engine.url)
    except Exception as e:
        print(e)
    os.system("alembic upgrade head")  # create all the tables
    celery.Task = get_celery_test_task()

    yield TestClient(app)

    base_db.engine.dispose()
    drop_database(base_db.engine.url)
