from fastapi import HTTPException, status

from app.common.error_enums import Errors, get_error_details
from app.common.logging import logger


class InsufficientPermission(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="insufficient permission",
        )


class ESException(Exception):
    """Exception capturing status_code from Client Request"""

    status_code = 0
    payload = ""

    def __init__(self, status_code, payload):
        self.status_code = status_code
        self.payload = payload
        Exception.__init__(
            self,
            "ES_Exception: status_code={}, payload={}".format(status_code, payload),
        )


class InvalidTokenError(Exception):
    pass


class InvalidGoogleRecaptcha(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=get_error_details(**Errors.INVALID_GOOGLE_RECAPTCHA),
        )


class CannotAcceptTheClosedApplication(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_error_details(**Errors.CANNOT_ACCEPT_THE_CLOSED_APPLICATION),
        )


class CannotRejectTheClosedApplication(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_error_details(**Errors.CANNOT_REJECT_THE_CLOSED_APPLICATION),
        )


class EmailOrPasswordIncorrect(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=get_error_details(**Errors.EMAIL_OR_PASSWORD_INCORRECT),
        )


class RefreshTokenIncorrect(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_error_details(**Errors.REFRESH_TOKEN_INCORRECT),
        )


class EmailIsAlreadyUsedInUser(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=get_error_details(**Errors.EMAIL_IS_ALREADY_USER_IN_USER),
        )


class NotImplemented(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=get_error_details(**Errors.NOT_IMPLEMENTED),
        )


class KeycloakUserNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_details(**Errors.USER_NOT_FOUND),
        )


# here we put the key as the uniq index name , the value as the exception to handle IntegrityError
INTEGRITY_ERRORS = {"ix_users_email": EmailIsAlreadyUsedInUser}


class KeycloakError(HTTPException):
    def __init__(self, msg: str | None = None):
        if msg is not None:
            logger.exception(msg)
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Request500(HTTPException):
    def __init__(self, msg: str | None = None):
        if msg is not None:
            logger.exception(msg)
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="services not available",
        )


class InvalidKeycloakRequest(HTTPException):
    def __init__(self, msg: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)


class EmailOrUsernameExist(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=get_error_details(**Errors.USER_EMAIL_OR_USERNAME_USED),
        )


class MobileExist(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=get_error_details(**Errors.USER_MOBILE_USED),
        )


class DuplicateRoleName(HTTPException):
    def __init__(self, msg: str | None = None):
        if msg is not None:
            logger.exception(msg)
        super().__init__(status_code=status.HTTP_409_CONFLICT)


class DuplicateGroupName(HTTPException):
    def __init__(self, msg: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=msg)


class NotFoundError(HTTPException):
    def __init__(self, msg: str = "item not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=msg)


class UserNotFound(HTTPException):
    def __init__(self, msg: str = "user not found"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)


class NotAllowedToChangePassword(HTTPException):
    def __init__(self, msg: str = "not allowed to change password"):
        super().__init__(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail=msg)


class InvalidGrant(HTTPException):
    def __init__(self, msg: str = "Account is not fully set up"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)


class RequestReachedLimitationApplication(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_error_details(**Errors.REQUEST_REACHED_LIMITATION_APPLICATION),
        )


class AlreadyReply(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_error_details(**Errors.ALREADY_REPLIED),
        )


class ThereIsNoApplication(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_error_details(**Errors.THERE_IS_NO_APPLICATION),
        )


class EmailExist(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=get_error_details(**Errors.USER_EMAIL_USED),
        )


class UsernameExist(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=get_error_details(**Errors.USER_USERNAME_USED),
        )
