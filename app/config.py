import os
from functools import lru_cache

from pydantic_settings import BaseSettings

from app.common.enums import LoggingLevel
from app.common.logging import logging


def fall_back_and_warn_if_none(env_name: str, default):
    value = os.environ.get(env_name)
    if value is None:
        logging.warning(f"{env_name} env is missing will fall back to {default}")
        value = default
    return default


class BaseConfig(BaseSettings):
    production: bool = False
    testing: bool = False
    ENVIRONMENT: str = "default"
    default_allow_origins: list[str] = ["*"]
    APP_NAME: str = "notification"
    ALLOWED_HOSTS: list[str] = ["*"]
    # timezone
    APP_TZ: str = "Asia/Riyadh"

    FORWARDED_ALLOW_IPS: str = "*"

    FEATURE_FLAG_LOCAL_CACHING_TTL: int = 5
    FEATURE_FLAG_LOCAL_CASH_SIZE_LIMIT: int = 100

    FILE_EXPORT_THRESHOLD: int = 1000
    
    '''
    this is our FCM connection
    
    '''
    GOOGLE_TYPE: str = "service_account"
    GOOGLE_PROJECT_ID: str = "the-garage-75c8c"
    GOOGLE_CLIENT_EMAIL: str = (
        "garage-calendar@the-garage-75c8c.iam.gserviceaccount.com"
    )
    GOOGLE_CLIENT_ID: str = "116604712848060127486"
    GOOGLE_CLIENT_X509_CERT_URL: str = (
        "https://www.googleapis.com/robot/v1/metadata/x509/garage-calendar%40the-garage-75c8c.iam.gserviceaccount.com"
    )
    GOOGLE_DELEGATION_EMAIL: str = "o.alwahiby@thegarage.sa"
    GOOGLE_PRIVATE_KEY: str = (
        "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDZ3YaE+a81A+8C\nELz2PI/MUXoFmFcLgVSs4Tzi2tIlOkm0Se7z3V4JApUedMqleYaIEn0fAtvJLkJq\n49R+Ef0TIz5yqmGWgdx3FtYoXAKeQqZc5/c0BWBlcPnukvatoxp4twNH1LtyN2bB\nZFsKabOKHlel9enu07n+02L576S8dEBTreqsueUyVCqNv7KrlRYoiOQ8RAznuMko\nq2UpZc0cniQuJR+XQNzkJWY8jB8SlfqJmNluMkyZI6V7tTNzc2P6QYgNAz1nh3DG\nJDLKLg7j5LKiVoJUNt+Wkq//JiVyaTx8NBraaJXyULwTcMwcyEMBebXWHeO6GRYu\nJmnHHwlVAgMBAAECggEAIjMLu8dfa94QixgfjDPDiu+QolzgmnYUhF2Ia5VX/u9g\nby8FQJNpAIG+8MdP9vErCiSE2Z+0P/zFVkwp/hmgICdHKpl5CjbxFGH+/4TksFKG\nv6Ig2bICXh+BoaQWRE7h3T3gA6BERdCmjl3M4Mc+ShnV6RUU7Mr1sSfJALJP/3j3\nO56v5MRMG+82YzCmUna+idynSvdwX4mUc4zIx93KnxbL0WqBWJeO5xPpx0WNkCae\nS8Od9VVoeXixMSe/95ljlnEcVOS+tjsFuSqLugMPUp6YuZV2awprJWGY9ApqQkjT\nyz+OxI5tPVt6YI3KW1fhoQ3ZJWue5uYKZCbG8/HYXQKBgQD9MrXVMYl2UVVF6KbL\nTrohti4Ubh5OlAo0RKO3iKAox9/9609K69BK3yrsK+YSbdjpyYnTBKgWPVFbx2y5\nPKUlMyiCIpviYmeDP1uowNX0LFAn740MA0lc0LqBAzhP0QaGLXMvfKygJEo4w6aZ\nA7p7xWLTOxKZ5yyjnra0he2lawKBgQDcRrhovZmr3T0LuDlXCB+AnMcHdKmQIlib\naltuG4DKuNMlTUlwsORJOcmGYuptSM26CTZGN2wftXM2wSyv4WtRVlSI+v3D6Epj\nwTilITjAEnNv8YPpL3zOSN/QjKVsIyeE4KQFKw6Sh9ewAtok73mJIj1NJQhYEdLs\n/FElzer8PwKBgQDbjCwlJ6YVRSMW0kxGwAYfkzPTnUSESFOszNPVIhAWLHIqX+7K\nfT2Inog+bzY5Rqyu04XBxyjk19iDJ6I74L0mS3zVkqLuovs00CxvYH5lEkOSzWHV\nR8hGRetiUON0OkBY+nIFfCrHVZBSNjxwM85w4k/17yQK9Ww8mDO+xt6w7wKBgQCa\nHPCQd3a4g8VeGbokZg6EUSv+z2SC70THF5Z4Zs2pB77Sbkxfh6Nwh/mzCCmz5Cfr\nbN6IKeaAGNdPC8BUHYaUFa53WAOLuU2ylVEoVyH5X+9b9sGvuAW93caZho2GJuJT\nWUfoRcOgSWJiRtyQ0utZQpdZDfvUgkPsgmvT40nwyQKBgAYwZbrqIoIpoUJPotvN\niMh0YxOy2iQEJCOy9DS3aNcIBymw+WzL2Z0dZ16HBYC87j8dNQ2vv8Ze0FVpj4gy\nNFvjl4S6e00+O7dmlTlwsXBh1Ph/DzDgSDtjdNj2K4LwaCxjHihtZrdkw5MnDryu\ndknPmwfrAwBokD03++4o0CV9\n-----END PRIVATE KEY-----\n"
    )
    GOOGLE_PRIVATE_KEY_ID: str = "ab357a5c5a017f6856ea5939f37878edd5cbc5f2"
    
    # keycloak configs
    KEYCLOAK_SERVER_URL: str = "http://keycloak:8080/"
    KEYCLOAK_CLIENT_ID: str = "notification-api"
    KEYCLOAK_REALM: str = "main"
    KEYCLOAK_CLIENT_SECRET: str = "BvCqeQgI1d9yh287aTwzsKVgFqrdWs3x"

    # credentials for the keycloak admin user who dose the actual requests to keycloak on behave of platform admins
    KEYCLOAK_ADMIN_USERNAME: str = "admin"
    KEYCLOAK_ADMIN_PASSWORD: str = "Password"
    # the max timeout after witch we will raise an error instad of more timeouts
    KEYCLOAK_ADMIN_LOGIN_TIMEOUT_LIMIT: int = 60
    
    
    # rides configs
    REDIS_HOST: str | None = None
    REDIS_PORT: int | None = None
    REDIS_DB: int | None = None
    REDIS_CASHING_TTL: int = 3600
    REDIS_LOCAL_CASHING_TTL: int = 2
    REDIS_LOCAL_CASH_SIZE_LIMIT: int = 1000
    REDIS_TIMEOUT: int = 500
    REDIS_CONNECTION_POOL_SIZE: int = 20
    REDIS_SOCKET_KEEPALIVE: bool = True
    
    # celery configs
    CELERY_RESULT_BACKEND: str | None = None
    CELERY_BROKER_URL: str | None = None
    ENABLE_CELERY_RETRY: bool = True
    ENABLE_CELERY_RETRY_BACKOFF: bool = True
    CELERY_RETRY_MAX: int = 10
    CELERY_RETRY_BACKOFF_MAX: int = 3600
    CELERY_ENABLE_RESULT_BACKEND: bool = False


    


    @property
    def allow_hosts(self):
        if os.environ.get("ALLOWED_HOSTS") is None:
            return self.default_allow_origins
        else:
            return os.environ.get("ALLOWED_HOSTS").split(",")

    @property
    def allow_core_origins(self):
        if os.environ.get("ALLOWED_CORS_ORIGINS") is None:
            return self.default_allow_origins
        else:
            return os.environ.get("ALLOWED_CORS_ORIGINS").split(",")

    openapi_url: str | None = "/openapi.json"
    docs_url: str = "/docs"


    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int
    
    READ_ONLY_DB_USER: str | None = None
    READ_ONLY_DB_PASSWORD: str | None = None
    READ_ONLY_DB_NAME: str | None = None
    READ_ONLY_DB_HOST: str | None = None
    READ_ONLY_DB_PORT: int | None = None


    ENABLE_CASHING: bool = True
    LOGGING_LEVEL: LoggingLevel = LoggingLevel.INFO
    RELEASE_SHA: str = "unknown"

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def SQLALCHEMY_READ_DATABASE_URL(self) -> str:
        if self.READ_ONLY_DB_USER is not None:
            user = self.READ_ONLY_DB_USER
            password = self.READ_ONLY_DB_PASSWORD
            host = self.READ_ONLY_DB_HOST
            port = self.READ_ONLY_DB_PORT
            name = self.READ_ONLY_DB_NAME
            return f"postgresql://{user}:{password}@{host}:{port}/{name}"
        else:
            return self.SQLALCHEMY_DATABASE_URL

    SQL_POOL_SIZE: int = 40
    SQL_POOL_OVERFLOW_SIZE: int = 10
    SQL_POOL_ENABLED: bool = True

    LECTURE_START: int = 32
    LECTURE_END: int = 95
    SLOT_TIME: int = 15

    class Config:
        env_file = ".env"


# you can set the defaults from here or over ride all using .env


class ProductionConfig(BaseConfig):
    production: bool = True
    testing: bool = False
    ENVIRONMENT: str = "prod"
    openapi_url: str | None = None


class StagingConfig(BaseConfig):
    production: bool = True
    testing: bool = False
    ENVIRONMENT: str = "staging"
    LOGGING_LEVEL: LoggingLevel = LoggingLevel.DEBUG


class TestingConfig(BaseConfig):
    production: bool = False
    testing: bool = True
    ENVIRONMENT: str = "testing"
    SQL_POOL_ENABLED: bool = False


@lru_cache()
def current_config(ProductionConfig, StagingConfig, TestingConfig, BaseConfig):
    """
    this will load the required config passed on STAGE env if not set it will load LocalConfig
    """
    stage = os.environ.get("ENVIRONMENT", "local")
    logging.info(f"loading {stage} Config...")

    if stage == "prod":
        config = ProductionConfig()
    elif stage == "staging":
        config = StagingConfig()
    elif stage == "testing":
        config = TestingConfig()
    elif stage == "local":
        config = BaseConfig()
    else:
        raise Exception(f"ENVIRONMENT: {stage} is not supported")

    return config


config: BaseConfig = current_config(
    ProductionConfig,
    StagingConfig,
    TestingConfig,
    BaseConfig,
)
