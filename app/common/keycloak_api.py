import datetime
from time import sleep
from typing import Dict, List, Optional

import requests
from fastapi.exceptions import HTTPException

from app.common.exceptions import (
    DuplicateGroupName,
    DuplicateRoleName,
    EmailOrPasswordIncorrect,
    EmailOrUsernameExist,
    InvalidGrant,
    KeycloakError,
    KeycloakUserNotFound,
    NotAllowedToChangePassword,
    NotFoundError,
    RefreshTokenIncorrect,
    Request500,
)
from app.common.logging import logger
from app.common.schemas import RolesRequest
from app.config import config

BASE_URL = config.KEYCLOAK_SERVER_URL
REALM = config.KEYCLOAK_REALM


def debug_response(response: requests.Response):
    if response.status_code >= 500:
        raise Request500()
    logger.debug(response.text)
    logger.debug(f"len(response.text): {len(response.text)}")
    logger.debug(f"response.content: {len(response.content)}")


def get_url_and_body_for_roles(
    group_id: str, roles_request: "RolesRequest", client_id_uuid: str | None = None
):
    is_client_role = client_id_uuid is not None
    if is_client_role:
        url = f"{BASE_URL}admin/realms/{REALM}/groups/{group_id}/role-mappings/clients/{client_id_uuid}"
    else:
        url = f"{BASE_URL}admin/realms/{REALM}/groups/{group_id}/role-mappings/realm"

    body = []
    for role in roles_request.roles:
        body_dict = {
            "id": role.id,
            "name": role.name,
            "composite": False,
            "clientRole": is_client_role,
            "containerId": f"{REALM}",
        }
        body.append(body_dict)
    return url, body


class KeycloakAdminApiService(object):
    """
    this services will use and mange keycloak admin api,
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if BASE_URL is None:
            raise Exception("BASE_URL is not known")

    def get_user(self, id: str):
        # docs https://www.keycloak.org/docs-api/15.0/rest-api/index.html#_getuser
        url = f"{BASE_URL}admin/realms/{REALM}/users/{id}"
        response = requests.get(url, headers=self._headers())

        if response.status_code == 401:
            # re-log in
            self._get_admin_token()
            # re-do the request
            response = requests.get(url, headers=self._headers())

        if response.status_code >= 500:
            raise Request500()

        if response.status_code == 404:
            raise KeycloakUserNotFound

        if response.status_code != 200:
            raise KeycloakError(
                msg=f"request get {url} returned a none 200 status ({response.status_code}), body: {response.text}"
            )
        user_info = response.json()
        logger.debug(f"user_info_by_id {user_info}")
        return user_info

    def create_realm_role(
        self,
        name: Optional[str] = None,
        attributes: Optional[dict] = None,
        clientRole: Optional[bool] = None,
        composite: Optional[bool] = None,
        composites: Optional[dict] = None,
        containerId: Optional[str] = None,
        description: Optional[str] = None,
        id: Optional[str] = None,
    ) -> None:
        # docs https://www.keycloak.org/docs-api/15.0/rest-api/index.html#_createrole
        url = f"{BASE_URL}admin/realms/{REALM}/roles"
        body = {
            "name": name,
            "attributes": attributes,
            "clientRole": clientRole,
            "composite": composite,
            "composites": composites,
            "containerId": containerId,
            "description": description,
            "id": id,
        }
        response = requests.post(url=url, json=body, headers=self._headers())
        if response.status_code != 201:
            if response.status_code == 409 and response.json()[
                "errorMessage"
            ].startswith("Role with name"):
                raise DuplicateRoleName
            logger.exception(
                f"got unexpected response from keycloak while creating role. body={body}"
            )
            raise KeycloakError

    def get_realm_role(
        self,
        brief_representation: bool = True,
        first: Optional[int] = None,
        max: Optional[int] = None,
        search: Optional[str] = None,
    ):
        # docs https://www.keycloak.org/docs-api/15.0/rest-api/index.html#_getroles
        """
        [
            {
            'id': '02f5adb7-916c-4763-bf5f-3c92b0abc594',
            'name': 'garage_admin',
            'description': 'garage admin he can create and review challenges',
            'composite': False,
            'clientRole': False,
            'containerId': 'main'
            }
        ]
        """
        url = f"{BASE_URL}admin/realms/{REALM}/roles"
        params = {
            "briefRepresentation": brief_representation,
            "first": first,
            "max": max,
            "search": search,
        }

        response = requests.get(url=url, params=params, headers=self._headers())
        if response.status_code != 200:
            logger.exception(
                f"got unexpected token from keycloak. url:{url}, max:{max}, search:{search}"
            )
            raise KeycloakError
        return response.json()

    def get_all_clients(self):
        url = f"{BASE_URL}admin/realms/{REALM}/clients"
        response = requests.get(url=url, headers=self._headers())
        if response.status_code != 200:
            raise KeycloakError
        return response.json()

    def create_new_client(
        self, client_id: str, client_base_url: str, client_redirect_urls: List[str]
    ):
        url = f"{BASE_URL}admin/realms/{REALM}/clients"
        params = {"max": 1000}
        body = {
            "clientId": client_id,
            "rootUrl": client_base_url,
            "redirectUris": client_redirect_urls,
        }
        response = requests.post(
            url=url, json=body, params=params, headers=self._headers()
        )

        if response.status_code >= 400:
            raise KeycloakError

    def create_user(self, rep: dict):
        # docs https://www.keycloak.org/docs-api/15.0/rest-api/index.html#_createuser
        url = f"{BASE_URL}admin/realms/{REALM}/users"
        response = requests.post(url=url, json=rep, headers=self._headers())
        debug_response(response)
        if len(response.text) > 0 and response.json().get("errorMessage") is not None:
            raise EmailOrUsernameExist

    def create_groups(
        self,
        name: str,
        roles: Optional[List[str]] = None,
        access: Optional[dict] = None,
        attributes: Optional[dict] = None,
        clientRoles: Optional[dict] = None,
        id: Optional[str] = None,
        subGroups: Optional[List[dict]] = None,
    ):
        # docs https://www.keycloak.org/docs-api/15.0/rest-api/index.html#_addtoplevelgroup
        url = f"{BASE_URL}admin/realms/{REALM}/groups"
        body = {
            "name": name,
            "realmRoles": roles,
            "access": access,
            "attributes": attributes,
            "clientRoles": clientRoles,
            "id": id,
            "subGroups": subGroups,
        }
        response = requests.post(url=url, json=body, headers=self._headers())
        debug_response(response)
        if response.status_code == 400:
            raise KeycloakError
        if len(response.content) != 0 and "errorMessage" in response.json():
            raise DuplicateGroupName(f"{response.json().get('errorMessage')}")

    def update_groups(
        self,
        id: str,
        name: Optional[str] = None,
        roles: Optional[List[str]] = None,
        access: Optional[dict] = None,
        attributes: Optional[dict] = None,
        clientRoles: Optional[dict] = None,
        subGroups: Optional[List[dict]] = None,
    ):
        # docs https://www.keycloak.org/docs-api/15.0/rest-api/index.html#_updategroup
        url = f"{BASE_URL}admin/realms/{REALM}/groups/{id}"
        body = {
            "name": name,
            "realmRoles": roles,
            "access": access,
            "attributes": attributes,
            "clientRoles": clientRoles,
            "id": id,
            "subGroups": subGroups,
        }
        response = requests.put(url=url, json=body, headers=self._headers())
        debug_response(response)
        if response.status_code == 404:
            raise NotFoundError(f"{response.json().get('error')}")
        if response.status_code == 400:
            raise KeycloakError
        if response.status_code == 409:
            raise DuplicateGroupName(f"{response.json().get('errorMessage')}")

    def get_group_by_id(
        self,
        id: str,
    ) -> Dict:
        # docs https://www.keycloak.org/docs-api/15.0/rest-api/index.html#_getgroup
        url = f"{BASE_URL}admin/realms/{REALM}/groups/{id}"
        response = requests.get(url=url, headers=self._headers())
        debug_response(response)
        if response.status_code == 400:
            raise KeycloakError
        if response.status_code == 404:
            raise NotFoundError(f"{response.json().get('error')}")
        return response.json()

    def delete_group_by_id(
        self,
        group_id: str,
    ) -> Dict:
        # docs https://www.keycloak.org/docs-api/15.0/rest-api/index.html#_deletegroup
        url = f"{BASE_URL}admin/realms/{REALM}/groups/{group_id}"
        response = requests.delete(url=url, headers=self._headers())
        debug_response(response)
        if response.status_code == 400:
            raise KeycloakError
        if response.status_code == 404:
            raise NotFoundError(f"{response.json().get('error')}")
        return response.json()

    def create_client_roles_protocol_mapper(self, client_id: str, client_scope_id: str):
        """
        {
            "id": "9623b054-e6df-45ac-9fee-bd607c86b19b",
            "name": "roles",
            "protocol": "openid-connect",
            "protocolMapper": "oidc-usermodel-client-role-mapper",
            "consentRequired": false,
            "config": {
                "multivalued": "true",
                "userinfo.token.claim": "false",
                "id.token.claim": "false",
                "access.token.claim": "true",
                "claim.name": "roles",
                "jsonType.label": "String",
                "usermodel.clientRoleMapping.clientId": "dashboard"
            }
        }
        https://stackoverflow.com/questions/66822016/where-are-all-of-the-keycloak-protocol-mapper-config-options-documented
        """
        body = {
            "name": "roles",
            "protocol": "openid-connect",
            "protocolMapper": "oidc-usermodel-client-role-mapper",
            "consentRequired": False,
            "config": {
                "multivalued": True,
                "userinfo.token.claim": False,
                "id.token.claim": False,
                "access.token.claim": True,
                "claim.name": "roles",
                "jsonType.label": "String",
                "usermodel.clientRoleMapping.clientId": client_id,
            },
        }
        url = f"{BASE_URL}admin/realms/{REALM}/clients/{client_scope_id}/protocol-mappers/models"
        response = requests.post(url=url, json=body, headers=self._headers())
        debug_response(response)
        if response.status_code != 201:
            if response.status_code == 409 and response.json()[
                "errorMessage"
            ].startswith("Protocol mapper exists"):
                raise DuplicateRoleName
            logger.exception(
                f"got unexpected response from keycloak while creating role. body={body}"
            )
            raise KeycloakError

    def get_groups(
        self,
        brief_representation: bool = True,
        first: Optional[int] = None,
        max: Optional[int] = None,
        search: Optional[str] = None,
    ) -> List[dict]:
        # docs https://www.keycloak.org/docs-api/15.0/rest-api/index.html#_getgroups
        url = f"{BASE_URL}admin/realms/{REALM}/groups"
        params = {
            "briefRepresentation": brief_representation,
            "first": first,
            "max": max,
            "search": search,
        }
        response = requests.get(url=url, params=params, headers=self._headers())
        if response.status_code != 200:
            logger.exception(
                f"got unexpected token from keycloak. url:{url}, max:{max}, search:{search}"
            )
            raise KeycloakError
        return response.json()

    def get_group_members(
        self,
        id: str,
        brief_representation: bool = True,
        first: Optional[int] = None,
        max: Optional[int] = None,
    ):
        params = {
            "briefRepresentation": brief_representation,
            "first": first,
            "max": max,
        }
        url = f"{BASE_URL}admin/realms/{REALM}/groups/{id}/members"
        response = requests.get(url=url, params=params, headers=self._headers())
        debug_response(response)
        if response.status_code == 400:
            raise KeycloakError
        if response.status_code == 404:
            raise NotFoundError(f"{response.json().get('error')}")
        return response.json()

    def create_client_role(
        self,
        client_id_uuid: str,
        name: Optional[str] = None,
        attributes: Optional[dict] = None,
        clientRole: Optional[bool] = None,
        composite: Optional[bool] = None,
        composites: Optional[dict] = None,
        containerId: Optional[str] = None,
        description: Optional[str] = None,
        id: Optional[str] = None,
    ) -> None:
        # docs https://www.keycloak.org/docs-api/15.0/rest-api/index.html#_createrole
        url = f"{BASE_URL}admin/realms/{REALM}/clients/{client_id_uuid}/roles"
        body = {
            "name": name,
            "attributes": attributes,
            "clientRole": clientRole,
            "composite": composite,
            "composites": composites,
            "containerId": containerId,
            "description": description,
            "id": id,
        }
        response = requests.post(url=url, json=body, headers=self._headers())
        if response.status_code != 201:
            if response.status_code == 409 and response.json()[
                "errorMessage"
            ].startswith("Role with name"):
                raise DuplicateRoleName
            logger.exception(
                f"got unexpected response from keycloak while creating role. body={body}"
            )
            raise KeycloakError

    def get_clients_roles(
        self,
        client_id_uuid: str,
        brief_representation: bool = True,
        first: Optional[int] = None,
        max: Optional[int] = None,
        search: Optional[str] = None,
    ):
        # docs https://www.keycloak.org/docs-api/15.0/rest-api/index.html#_getroles
        """
        [
            {
            'id': '02f5adb7-916c-4763-bf5f-3c92b0abc594',
            'name': 'coderhub_admin',
            'description': 'coderhub admin he can create and review challenges',
            'composite': False,
            'clientRole': False,
            'containerId': 'main'
            }
        ]
        """

        url = f"{BASE_URL}admin/realms/{REALM}/clients/{client_id_uuid}/roles"
        params = {
            "briefRepresentation": brief_representation,
            "first": first,
            "max": max,
            "search": search,
        }

        response = requests.get(url=url, params=params, headers=self._headers())
        debug_response(response)
        if response.status_code != 200:
            logger.exception(
                f"got unexpected token from keycloak. url:{url}, max:{max}, search:{search}"
            )
            raise KeycloakError
        return response.json()

    def join_group(self, id: str, group_id: str):
        # docs https://www.keycloak.org/docs-api/15.0/rest-api/index.html#_joingroup
        url = f"{BASE_URL}admin/realms/{REALM}/users/{id}/groups/{group_id}"

        response = requests.put(url, headers=self._headers())
        debug_response(response)
        if response.status_code == 404:
            if response.json()["error"] == "Group not found":
                raise HTTPException(
                    status_code=404,
                    detail="group not found please check the passed group name",
                )
            if response.json()["error"] == "User not found":
                raise HTTPException(
                    status_code=404, detail="user not found please check the passed id"
                )
            else:
                logger.exception(f"unhandled error {response.json()['error']}")

    def delete_group(self, id: str):
        # docs https://www.keycloak.org/docs-api/15.0/rest-api/index.html#_deletegroup
        url = f"{BASE_URL}admin/realms/{REALM}/groups/{id}"
        response = requests.delete(url=url, headers=self._headers())
        debug_response(response)
        if response.status_code == 404:
            raise NotFoundError(f"{response.json().get('error')}")
        if response.status_code == 400:
            raise KeycloakError

    def remove_membership(self, id: str, group_id: str):
        # docs https://www.keycloak.org/docs-api/15.0/rest-api/index.html#_removemembership
        url = f"{BASE_URL}admin/realms/{REALM}/users/{id}/groups/{group_id}"
        response = requests.delete(url, headers=self._headers())
        debug_response(response)
        if response.status_code == 404:
            if response.json()["error"] == "Group not found":
                raise HTTPException(
                    status_code=404,
                    detail="group not found please check the passed group name",
                )
            if response.json()["error"] == "User not found":
                raise HTTPException(
                    status_code=404, detail="user not found please check the passed id"
                )
            else:
                logger.exception(f"unhandled error {response.json()['error']}")

    def add_roles_to_group(
        self,
        group_id: str,
        roles_request: "RolesRequest",
        client_id_uuid: str | None = None,
    ):
        # docs https://www.keycloak.org/docs-api/15.0/rest-api/index.html#_addrealmrolemappings
        url, body = get_url_and_body_for_roles(
            client_id_uuid=client_id_uuid,
            roles_request=roles_request,
            group_id=group_id,
        )
        response = requests.post(url=url, json=body, headers=self._headers())
        if response.status_code == 404:
            raise NotFoundError(f"{response.json().get('error')}")

    def remove_roles_from_group(
        self,
        group_id: str,
        roles_request: "RolesRequest",
        client_id_uuid: str | None = None,
    ):
        # docs https://www.keycloak.org/docs-api/15.0/rest-api/index.html#_deleterealmrolemappings
        url, body = get_url_and_body_for_roles(
            client_id_uuid=client_id_uuid,
            roles_request=roles_request,
            group_id=group_id,
        )
        response = requests.delete(url=url, json=body, headers=self._headers())
        debug_response(response)
        if response.status_code == 404:
            raise NotFoundError(f"{response.json().get('error')}")
        if response.status_code == 400:
            raise KeycloakError

    def get_group_available_roles(self, group_id: str):
        # docs https://www.keycloak.org/docs-api/15.0/rest-api/index.html#_getavailablerealmrolemappings
        # get all roles dose not assign to this group
        url = f"{BASE_URL}admin/realms/{REALM}/groups/{group_id}/role-mappings/realm/available"
        response = requests.get(url=url, headers=self._headers())
        debug_response(response)
        if response.status_code == 404:
            raise NotFoundError(f"{response.json().get('error')}")
        if response.status_code == 400:
            raise KeycloakError
        return response.json()

    def get_users(
        self,
        brief_representation: bool = False,
        email: Optional[str] = None,
        email_verified: Optional[bool] = None,
        enabled: Optional[bool] = None,
        exact: Optional[bool] = None,
        first: Optional[int] = None,
        name: Optional[str] = None,
        idp_alias: Optional[str] = None,
        idp_user_id: Optional[str] = None,
        max: int = 100,
        search: Optional[str] = None,
        username: Optional[str] = None,
    ) -> List[dict]:
        # docs https://www.keycloak.org/docs-api/15.0/rest-api/index.html#_getusers
        url = f"{BASE_URL}admin/realms/{REALM}/users"
        params = {
            "briefRepresentation": brief_representation,
            "email": email,
            "emailVerified": email_verified,
            "enabled": enabled,
            "exact": exact,
            "first": first,
            "name": name,
            "idpAlias": idp_alias,
            "idpUserId": idp_user_id,
            "max": max,
            "search": search,
            "username": username,
        }

        response = requests.get(url=url, params=params, headers=self._headers())
        if response.status_code >= 500:
            raise Request500()
        users_info = response.json()
        return users_info

    def _headers(self):
        access_token = self.current_token["access_token"]
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    _current_token: Optional[dict] = None

    @property
    def current_token(self):
        if self._current_token is None:
            self._get_admin_token()
            return self._current_token

        if datetime.datetime.now() >= self._current_token["expires_at"]:
            self._refresh_current_token()

        return self._current_token

    @current_token.setter
    def current_token(self, token: dict):
        now = datetime.datetime.now()
        expires_in = datetime.timedelta(seconds=token["expires_in"])
        buffer = datetime.timedelta(milliseconds=100)
        token["expires_at"] = now + expires_in - buffer
        self._current_token = token

    def _get_admin_token(self, timeout: float = 1):
        logger.info(f"login {config.KEYCLOAK_ADMIN_USERNAME}")
        url = f"{BASE_URL}realms/{REALM}/protocol/openid-connect/token"
        body = {
            "client_id": config.KEYCLOAK_CLIENT_ID,
            "grant_type": "password",
            "client_secret": config.KEYCLOAK_CLIENT_SECRET,
            "username": config.KEYCLOAK_ADMIN_USERNAME,
            "password": config.KEYCLOAK_ADMIN_PASSWORD,
        }

        response = requests.post(url, data=body)
        if response.status_code >= 500:
            if timeout > config.KEYCLOAK_ADMIN_LOGIN_TIMEOUT_LIMIT:
                raise Request500(
                    f"timeout limit exceeded ({timeout} > {config.KEYCLOAK_ADMIN_LOGIN_TIMEOUT_LIMIT})"
                )
            logger.warning(f"failed to login for super admin, retry timeout: {timeout}")
            sleep(timeout)
            self._get_admin_token(timeout=timeout * 1.5)
        else:
            self.current_token = response.json()

    def _refresh_current_token(self):
        logger.info("_refresh_current_token...")
        url = f"{BASE_URL}realms/{REALM}/protocol/openid-connect/token"

        body = {
            "client_id": config.KEYCLOAK_CLIENT_ID,
            "grant_type": "refresh_token",
            "client_secret": config.KEYCLOAK_CLIENT_SECRET,
            "refresh_token": self._current_token["refresh_token"],
        }

        response = requests.post(url, data=body)
        if response.status_code != 200:
            self._get_admin_token()
        else:
            self.current_token = response.json()

    def user_login(
        self,
        username: str,
        password: str,
        timeout: float = 1,
        remember_me: bool | None = False,
    ):
        import copy

        # URL for token endpoint
        url = f"{BASE_URL}realms/{REALM}/protocol/openid-connect/token"
        # Authenticate the user and get user tokens
        body = {
            "client_id": config.KEYCLOAK_CLIENT_ID,
            "username": username,
            "password": password,
            "client_secret": config.KEYCLOAK_CLIENT_SECRET,
            "grant_type": "password",
            "scope": "offline_access" if remember_me else None,
        }
        headers = copy.deepcopy(self._headers())
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        user_response = requests.post(url, data=body)

        if user_response.status_code >= 500:
            if timeout > config.KEYCLOAK_ADMIN_LOGIN_TIMEOUT_LIMIT:
                raise Request500(
                    f"timeout limit exceeded ({timeout} > {config.KEYCLOAK_ADMIN_LOGIN_TIMEOUT_LIMIT})"
                )
            logger.warning(f"failed to login for super admin, retry timeout: {timeout}")
            sleep(timeout)
            self.user_login(timeout=timeout * 1.5, username=username, password=password)
        elif user_response.status_code == 401:
            raise EmailOrPasswordIncorrect
        elif (
            user_response.status_code == 400
            and user_response.json()["error"] == "invalid_grant"
        ):
            raise InvalidGrant
        else:
            self.user_tokens = user_response.json()
        return self.user_tokens

    def user_refresh_token(self, refresh_token: str):
        url = f"{BASE_URL}realms/{REALM}/protocol/openid-connect/token"

        token_data = {
            "client_id": config.KEYCLOAK_CLIENT_ID,
            "client_secret": config.KEYCLOAK_CLIENT_SECRET,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        response = requests.post(url, data=token_data)
        if response.status_code == 200:
            token_response = response.json()
            new_access_token = token_response.get("access_token")
            new_refresh_token = token_response.get("refresh_token")
            expires_in = token_response.get("expires_in")
            refresh_expires_in = token_response.get("refresh_expires_in")
            refresh_token = token_response.get("refresh_token")

        elif response.status_code == 400:
            raise RefreshTokenIncorrect

        else:
            return ""

        return {
            "access_token": new_access_token,
            "expires_in": expires_in,
            "refresh_expires_in": refresh_expires_in,
            "refresh_token": refresh_token,
            "new_refresh_token": new_refresh_token,
        }

    def change_password(self, body):
        user_info = self.get_users(email=body.email, exact=True)
        if not user_info:
            raise KeycloakUserNotFound("User not found")

        user_id = user_info[0]["id"]

        if "UPDATE_PASSWORD" not in user_info[0]["requiredActions"]:
            raise NotAllowedToChangePassword

        url = f"{BASE_URL}admin/realms/{REALM}/users/{user_id}/reset-password"

        body = {
            "type": "password",
            "temporary": False,
            "value": body.new_password,
        }

        response = requests.put(url, json=body, headers=self._headers())
        debug_response(response)

        if response.status_code == 204:
            return {"message": "Password changed successfully"}
        elif response.status_code == 404:
            raise KeycloakUserNotFound("User not found")
        else:
            raise KeycloakError(f"Failed to change password: {response.text}")

    def reset_password(self, body):
        user_info = self.get_users(email=body.email, exact=True)
        if not user_info:
            raise KeycloakUserNotFound("User not found")

        user_id = user_info[0]["id"]

        url = f"{BASE_URL}admin/realms/{REALM}/users/{user_id}/reset-password"

        body = {
            "type": "password",
            "temporary": False,
            "value": body.new_password,
        }

        response = requests.put(url, json=body, headers=self._headers())
        debug_response(response)

        if response.status_code == 204:
            return {"message": "Password changed successfully"}
        elif response.status_code == 404:
            raise KeycloakUserNotFound("User not found")
        else:
            raise KeycloakError(f"Failed to change password: {response.text}")


keycloak_admin_api_service = KeycloakAdminApiService()
