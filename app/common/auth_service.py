from typing import Any

import requests
from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from redis.client import Redis
from sentry_sdk import set_user

from app.config import BaseConfig

from .exceptions import InsufficientPermission, InvalidTokenError
from .logging import logger


class CurrentUser(BaseModel):
    token: str
    id: str
    groups: list[str]
    email_verified: bool
    client_id: str | None
    email: str | None

    def is_admin(self, require_one_of: list[str] = [], require_all_of: list[str] = []):
        required_one_groups_set = set(require_one_of)
        required_all_groups_set = set(require_all_of)
        groups_set = set(self.groups)

        has_one_required_groups = (
            len(groups_set.intersection(required_one_groups_set)) > 0
        )
        has_all_required_groups = len(
            groups_set.intersection(required_all_groups_set)
        ) == len(required_all_groups_set)
        return has_one_required_groups and has_all_required_groups


class AuthService(object):
    token_info: dict[str, Any] | None = None
    token: str | None = None
    pub_key: str | None = None
    redis_client: Redis | None = None
    config: BaseConfig

    def __init__(
        self,
        server_url: str,
        client_id: str,
        realm_name: str,
        redis_host: str | None,
        redis_port: int | None,
        redis_db: int | None,
        config: BaseConfig,
    ) -> None:
        self.realm_name = realm_name
        self.server_url = server_url
        self.client_id = client_id

        if redis_host is not None:
            assert redis_port is not None, "we have redis_host but no redis_port!"
            assert redis_db is not None, "we have redis_host but no redis_db!"
            self.with_redis = True
            self.redis_client = Redis(host=redis_host, port=redis_port, db=redis_db)

        self.config = config
        # NOTE: if we're in testing we don't need the public key
        if not self.config.testing:
            self._get_pub_key()

    def id(self):
        """
        will abort if the headers contain a token but it's invalid ,
        method name kept from legacy
        :return: the current user id or None if the user isn't logged in
        """
        if not self.token:
            return None

        return self.token_info.get("sub")

    def groups(self):
        """
        will abort if the headers contain a token but it's invalid ,
        method name kept from legacy
        :return: the current user groups list or empty list if the user isn't logged in
        """
        if not self.token:
            return []

        return self.token_info.get("realm_access", {}).get("roles", [])

    def email_verified(self):
        if not self.token:
            return False

        return self.token_info.get("email_verified")

    def token_client_id(self):
        if not self.token:
            return False

        return self.token_info.get("clientId")

    def email(self):
        if not self.token:
            return False

        return self.token_info.get("email")

    def set_and_validate_token(self, token: str):
        if token is not None:
            self.token = token
            self._update_token_info()
            assert (
                self.token_info is not None
            ), "after self._update_token_info(), token_info must not be none"
            # set data for sentry reports
            set_user(
                {
                    "username": self.token_info.get("preferred_username"),
                    "id": self.token_info.get("sub"),
                    "email": self.token_info.get("email"),
                    "groups": self.token_info.get("realm_access", {}).get("roles", []),
                }
            )
        else:
            set_user({"username": "unknown"})

    def _update_token_info(self):
        try:
            # NOTE: if we're in testing we don't to verify the signature and expiration
            if self.config.testing:
                self.token_info = jwt.get_unverified_claims(token=self.token)
                return None

            self.token_info = jwt.decode(
                token=self.token,
                key=self._get_pub_key(),
                algorithms=["RS256"],
                options={"verify_aud": False},
            )

        except Exception:
            raise InvalidTokenError

    def _get_pub_key(self):
        if self.pub_key is not None:
            return self.pub_key

        key_from_redis = (
            self.redis_client.get("KEYCLOAK_PUB_KEY") if self.with_redis else None
        )

        # if key_from_redis is None:
        #     logger.info("pub key redis miss!, calling keycloak")
        #     response = requests.get(f"{self.server_url}realms/{self.realm_name}")
        #     pub_key = response.json()["public_key"]
        #     self.pub_key = (
        #         f"-----BEGIN PUBLIC KEY-----\n{pub_key}\n-----END PUBLIC KEY-----"
        #     )
        #     if self.with_redis:
        #         self.redis_client.set("KEYCLOAK_PUB_KEY", self.pub_key, ex=3600)
        # else:
        #     self.pub_key = key_from_redis.decode("utf-8")

        return self.pub_key

    def login_required(self, groups=None):
        """
        a dependance to be used to stop access if the reqest don't have a token from one of our front clients,
        we can set allwed groups or leave it to allow any logged in user, with valid token
        Depends(AuthService.login_required()) or Depends(AuthService.login_required(['admin']))
        """

        def login_required_dependence(current_user: CurrentUser = Depends(self.current_user())):  # type: ignore[assignment]
            if current_user is None:
                raise HTTPException(status_code=401, detail="user not logged in")

            if groups is not None and len(groups) != 0:
                # look for at least one required group in the user groups if not found raise error
                if not current_user.is_admin(require_one_of=groups):
                    raise InsufficientPermission

        return login_required_dependence

    def client_required(self, clients: list[str] | None = None):
        """
        a dependance to be used to stop access if the reqest don't have a token from one of our backend clients,
        or we can set the allowed clients
        Depends(AuthService.client_required()) or Depends(AuthService.login_required(['admin']))
        """

        def client_required_dependence(current_user: CurrentUser = Depends(self.current_user())):  # type: ignore[assignment]
            if current_user is None:
                raise HTTPException(401, detail="user not logged in")
            assert (
                self.token_info is not None
            ), "if current user is not None, token_info must not be none!"
            client_id = self.token_info.get("clientId")
            if client_id is None:
                # the token wasn't genrated from a backend client
                raise InsufficientPermission

            if clients is not None and len(clients) != 0:
                allowed_clients = set(clients)
                if client_id not in allowed_clients:
                    raise InsufficientPermission

        return client_required_dependence

    def current_user(self):
        tokenUrl = (
            f"{self.server_url}realms/{self.realm_name}/protocol/openid-connect/token/"
        )
        token_schema = OAuth2PasswordBearer(tokenUrl, auto_error=False)

        def current_user_dependence(token: str = Depends(token_schema)) -> CurrentUser:  # type: ignore[assignment]
            if token is None:
                return None

            try:
                self.set_and_validate_token(token)
                return CurrentUser(
                    token=token,
                    id=self.id(),
                    groups=self.groups(),
                    email_verified=self.email_verified(),
                    client_id=self.token_client_id(),
                    email=self.email(),
                )
            except InvalidTokenError as error:
                try:
                    unverified_token = jwt.get_unverified_claims(token=token)
                except JWTError:
                    raise HTTPException(status_code=401, detail="invalid token")

                client_id = unverified_token.get("clientId")

                if client_id is not None:
                    logger.exception(
                        "user_token consist clientId",
                        extra=dict(error=error, client_id=client_id, token=token),
                    )
                raise HTTPException(status_code=401, detail="invalid token")

        return current_user_dependence
