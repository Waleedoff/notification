def get_error_details(error_code: str, error_message: str, data: dict = {}):
    return {"error_code": error_code, "error_message": error_message, "data": data}


class Errors:
    @classmethod
    def list(cls):
        result = []
        for key, value in cls.__dict__.items():
            if (
                not key.startswith("_")
                and not isinstance(value, classmethod)
                and not callable(value)
            ):
                result.append({**value, "error_name": key})
        return result

    # common
    USER_NOT_FOUND = {
        "error_code": "common_1",
        "error_message": "user not found please check the passed id",
    }
    USER_EMAIL_OR_USERNAME_USED = {
        "error_code": "common_2",
        "error_message": "اسم المستخدم او البريد الالكتروني مستعمل",
    }
    USER_MOBILE_USED = {
        "error_code": "common_3",
        "error_message": "mobile number already used",
    }
    EMAIL_IS_ALREADY_USER_IN_USER = {
        "error_code": "common_4",
        "error_message": "this email is already used by another user",
    }
    EMAIL_OR_PASSWORD_INCORRECT = {
        "error_code": "common_5",
        "error_message": "email or password incorrect",
    }
    REFRESH_TOKEN_INCORRECT = {
        "error_code": "common_6",
        "error_message": "refresh token incorrect",
    }
    NOT_IMPLEMENTED = {
        "error_code": "common_7",
        "error_message": "not implemented",
    }
    INVALID_GOOGLE_RECAPTCHA = {
        "error_code": "common_8",
        "error_message": "recaptcha is not valid",
    }
    CANNOT_ACCEPT_THE_CLOSED_APPLICATION = {
        "error_code": "common_9",
        "error_message": "Application that have been closed cannot be accept",
    }
    CANNOT_REJECT_THE_CLOSED_APPLICATION = {
        "error_code": "common_10",
        "error_message": "Application that have been closed cannot be reject",
    }
    REQUEST_REACHED_LIMITATION_APPLICATION = {
        "error_code": "common_11",
        "error_message": "you've reached limit of application",
    }
    ALREADY_REPLIED = {
        "error_code": "common_12",
        "error_message": "already replied",
    }
    THERE_IS_NO_APPLICATION = {
        "error_code": "common_13",
        "error_message": "there is no application",
    }
    USER_EMAIL_USED = {
        "error_code": "common_14",
        "error_message": "email already used",
    }
    USER_USERNAME_USED = {
        "error_code": "common_15",
        "error_message": "username already used",
    }
    THEMES_COUNT_LIMIT = {
        "error_code": "common_16",
        "error_message": "Themes maximum count should be two , delete one to add new theme",
    }
    # OTHER
    ECOSYSTEM_HAVE_ONE = {
        "error_code": "other_1",
        "error_message": "The maximum number of ecosystem is 1",
    }

    NO_CONTACT = {
        "error_code": "other-2",
        "error_message": "not contact in the database",
    }

    OPEN_CONTACT = {
        "error_code": "other-3",
        "error_message": "the contact is already opened",
    }
    CLOSE_CONTACT = {
        "error_code": "other-4",
        "error_message": "the contact is already closed",
    }

    DUPLICATE_CONTACT = {
        "error_code": "other-5",
        "error_message": "you cannot create a duplicate contact in the database",
    }

    INVALID_FCM_TOKEN = {
        "error_code": "other-6",
        "error_message": "invalid FCM token",
    }

    # PLUS
    PLUS_SHARE_OPINION_PUBLISHED_ALREADY = {
        "error_code": "plus_1",
        "error_message": "plus share opinion published already",
    }

    PLUS_SHARE_OPINION_UNPUBLISHED_ALREADY = {
        "error_code": "plus_2",
        "error_message": "plus share opinion unpublished already",
    }
    PLUS_ALREADY_PUBLISHED = {
        "error_code": "plus_3",
        "error_message": "plus already published",
    }
    PLUS_ALREADY_DRAFT = {
        "error_code": "plus_4",
        "error_message": "plus already draft",
    }
    PLUS_HAS_NO_APPLICATIONS = {
        "error_code": "plus-5",
        "error_message": "plus has no applications",
    }
    INVALID_PLUS_NUMBER = {
        "error_code": "plus-6",
        "error_message": "plus number is not found",
    }
    # INCUBATOR
    INCUBATOR_ALREADY_PUBLISHED = {
        "error_code": "incubator-1",
        "error_message": "incubator already published",
    }
    INCUBATOR_ALREADY_DRAFT = {
        "error_code": "incubator-2",
        "error_message": "incubator already draft",
    }
    INCUBATOR_HAS_NO_APPLICATIONS = {
        "error_code": "incubator-3",
        "error_message": "incubator has no applications",
    }

    # DISRUPT
    DISRUPT_ALREADY_PUBLISHED = {
        "error_code": "disrupt-1",
        "error_message": "disrupt already published",
    }
    DISRUPT_ALREADY_DRAFT = {
        "error_code": "disrupt-2",
        "error_message": "disrupt already draft",
    }
    DISRUPT_HAS_NO_APPLICATIONS = {
        "error_code": "disrupt-3",
        "error_message": "disrupt has no applications",
    }
    THERE_IS_NO_DISRUPT = {
        "error_code": "disrupt-4",
        "error_message": "there is no disrupt",
    }
    BIGGER_DISRUPT = {
        "error_code": "disrupt-5",
        "error_message": "the disrupt version is not found",
    }
    # COMMUNITY
    DUPLICATE_TOUR = {
        "error_code": "community-1",
        "error_message": "you cannot create a duplicate tour in the database",
    }
    NO_TOUR = {
        "error_code": "community-2",
        "error_message": "no tour in the database",
    }
    CLOSE_TOUR = {
        "error_code": "community-3",
        "error_message": "the tour is already closed",
    }
    OPEN_TOUR = {
        "error_code": "community-4",
        "error_message": "the tour is already opened",
    }
    TOUR_HAS_NO_APPLICATIONS = {
        "error_code": "community-5",
        "error_message": "tour has no applications",
    }
    DUPLICATE_PARTNER = {
        "error_code": "community-6",
        "error_message": "you cannot create a duplicate partner in the database",
    }
    NO_PARTNER = {
        "error_code": "community-7",
        "error_message": "no partner in the database",
    }

    OPEN_PARTNER = {
        "error_code": "community-8",
        "error_message": "the partner is already opened",
    }

    CLOSE_PARTNER = {
        "error_code": "community-9",
        "error_message": "the partner is already close",
    }

    DUPLICATE_EVENT = {
        "error_code": "community-10",
        "error_message": "you cannot create a duplicate event in the database",
    }
    NO_EVENT = {
        "error_code": "community-11",
        "error_message": "no event in the database",
    }

    OPEN_EVENT = {
        "error_code": "community-12",
        "error_message": "the event is already opened",
    }

    CLOSE_EVENT = {
        "error_code": "community-13",
        "error_message": "the event is already close",
    }

    EVENT_HAS_NO_APPLICATIONS = {
        "error_code": "community-14",
        "error_message": "event has no applications",
    }
    PARTNER_HAS_NO_APPLICATIONS = {
        "error_code": "community-15",
        "error_message": "partner has no applications",
    }

    # VISIT
    VISIT_ALREADY_EXISTS = {
        "error_code": "visit-1",
        "error_message": "visit already exists",
    }
    NO_VISIT_FOUND = {
        "error_code": "visit-2",
        "error_message": "no visit found",
    }
    VISIT_ALREADY_OPEN = {
        "error_code": "visit-3",
        "error_message": "visit already open",
    }
    VISIT_ALREADY_CLOSED = {
        "error_code": "visit-4",
        "error_message": "visit already closed",
    }
    VISIT_HAS_NO_APPLICATION = {
        "error_code": "visit-5",
        "error_message": "visit has no application",
    }
    VISIT_PERMISSION_EXPIRED = {
        "error_code": "visit-6",
        "error_message": "The QR code's acceptance period has expired",
    }
    VISIT_INVALID_QR = {
        "error_code": "visit-7",
        "error_message": "This QR code is invalid",
    }
    # UPLOAD
    ASSET_NAME_DOSE_NOT_INCLUDE_FILE_EXTENSION = {
        "error_code": "upload-1",
        "error_message": "asset name does not include file extension",
    }
    ASSET_NAME_ALREADY_EXIST = {
        "error_code": "upload-2",
        "error_message": "asset name already exist",
    }

    # USER
    USER_ALREADY_IN_THIS_GROUP = {
        "error_code": "user-1",
        "error_message": "user already in this group",
    }
    ROLE_NOT_EXIST_IN_REALM = {
        "error_code": "user-2",
        "error_message": "role not exist in realm",
    }
    ROLE_ALREADY_EXIST_IN_REALM = {
        "error_code": "user-3",
        "error_message": "role already exist in realm",
    }
    CANNOT_SEND_RESET_PASSWORD_EMAIL = {
        "error_code": "user-4",
        "error_message": "Unable to send reset password email. Please wait 2 hours after your initial request.",
    }
    INCORRECT_KEY = {
        "error_code": "user-5",
        "error_message": "incorrect key",
    }
    CANNOT_RESET_PASSWORD = {
        "error_code": "user-6",
        "error_message": "can not reset password, it is expired",
    }
    # SCANNER
    GARAGE_EVENT_IS_CLOSED = {
        "error_code": "scanner-1",
        "error_message": "garage event is closed",
    }

    QR_ALREADY_SCANNED = {
        "error_code": "scanner-2",
        "error_message": "barcode already scanned",
    }

    # ACTIVITY
    ACTIVITY_ALREADY_PUBLISH = {
        "error_code": "activity-1",
        "error_message": "activity already publish",
    }

    VERSION_IS_NONE_AND_TYPE_IS_NOT_NONE = {
        "error_code": "activity-2",
        "error_message": "version is require",
    }

    TYPE_IS_NONE_AND_VERSION_IS_NOT_NONE = {
        "error_code": "activity-3",
        "error_message": "type is require",
    }

    ACTIVITY_ALREADY_DRAFT = {
        "error_code": "activity-4",
        "error_message": "activity already draft",
    }

    # CONSULTATION
    CONSULTATION_ALREADY_PUBLISH = {
        "error_code": "consultation-1",
        "error_message": "consultation already published",
    }
    CONSULT_HAS_NO_APPLICATIONS = {
        "error_code": "consultation-2",
        "error_message": "consultation has no application",
    }
    CONSULTATION_ALREADY_DRAFT = {
        "error_code": "consultation-3",
        "error_message": "consultation already draft",
    }
    CONSULTATION_NUMBER_ALREADY_EXIST = {
        "error_code": "consultation-4",
        "error_message": "consultation number already exist",
    }
    CONSULTATION_NUMBER_GREATER_THAN_ONE = {
        "error_code": "consultation-5",
        "error_message": "consultation number it not must be greater than last consult number by more than 1",
    }
    PUBLISH_CONSULTATION_CAN_NOT_BE_DELETED = {
        "error_code": "consultation-6",
        "error_message": "a consultation that has been made published cannot be removed",
    }
    THE_CONSULTATION_NUMBER_MUST_EXCEED_ONE = {
        "error_code": "consultation-7",
        "error_message": "the consultation number must exceed one",
    }
    THE_LAST_CONSULTATION_CANNOT_BE_DELETED = {
        "error_code": "consultation-8",
        "error_message": "the last consultation cannot be deleted",
    }

    # BUILDING
    BUILDING_ALREADY_EXIST = {
        "error_code": "building-1",
        "error_message": "building already exist",
    }
    DUPLICATE_FLOOR_NUMBER_OR_NAME = {
        "error_code": "building-2",
        "error_message": "duplicate floor number or name",
    }
    DUPLICATE_RESOURCE_NUMBER = {
        "error_code": "building-3",
        "error_message": "duplicate resource number",
    }
    CANNOT_CREATE_FLOOR_WITHOUT_BUILDING = {
        "error_code": "building-4",
        "error_message": "can not create floor without building",
    }
    CANNOT_CREATE_RESOURCE_WITHOUT_FLOOR = {
        "error_code": "building-4",
        "error_message": "can not create resource without floor",
    }
    DUPLICATE_RESOURCE_CALENDAR_ID = {
        "error_code": "building-5",
        "error_message": "duplicate resource calendar id",
    }
    CAN_NOT_CHANGE_CALENDAR_ID = {
        "error_code": "building-6",
        "error_message": "can not change calendar id",
    }
    DATE_IS_IN_PAST = {
        "error_code": "building-7",
        "error_message": "date is in the past",
    }
    # BOOKING
    DUPLICATE_BOOKING = {
        "error_code": "booking-1",
        "error_message": "There is currently a booking, thus you are unable to create one.",
    }
    BOOKING_ALREADY_CANCELED = {
        "error_code": "booking-2",
        "error_message": "booking already canceled",
    }
    FOR_THIS_BOOKING_THERE_IS_NO_RESOURCE = {
        "error_code": "booking-3",
        "error_message": "For this booking, there is no resource.",
    }
    THIS_RESOURCE_DOES_NOT_ALLOW_RESERVATIONS_TO_BE_MADE = {
        "error_code": "booking-4",
        "error_message": "This resource does not allow reservations to be made",
    }
    EVENT_NOT_FOUND = {
        "error_code": "booking-5",
        "error_message": "event not found",
    }
    PAST_BOOKING_CANNOT_BE_DELETED = {
        "error_code": "booking-6",
        "error_message": "past booking can not be deleted",
    }
    PAST_BOOKING_CANNOT_BE_UPDATED = {
        "error_code": "booking-7",
        "error_message": "past booking can not be updated",
    }
    GOOGLE_ERROR = {
        "error_code": "booking-8",
        "error_message": "there seems to be an error while connecting to the Google client.",
    }
    EXPIRED_BOOKING = {
        "error_code": "booking-9",
        "error_message": "booking is expired",
    }
    PERMISSION_REQUIRED_TO_BOOK_THIS_RESOURCE = {
        "error_code": "booking-10",
        "error_message": "permission required to book this resource",
    }
    RESOURCE_MANAGEMENT_IS_NOT_ALLOWED = {
        "error_code": "booking-11",
        "error_message": "resource management is not allowed",
    }
    RESOURCE_CANNOT_BE_BOOKED = {
        "error_code": "booking-12",
        "error_message": "resource cannot be booked",
    }
    # HUB
    ORGANIZATION_ALREADY_EXIST = {
        "error_code": "organization-1",
        "error_message": "organization already exist",
    }
    CAN_NOT_CREATE_PROGRAM_WITHOUT_ORGANIZATION = {
        "error_code": "organization-2",
        "error_message": "can not create program without organization",
    }
    PROGRAM_ALREADY_EXIST = {
        "error_code": "organization-3",
        "error_message": "program already exist",
    }
    COMPANY_NAME_ALREADY_EXIST = {
        "error_code": "organization-4",
        "error_message": "company name already exist",
    }
    COMPANY_EMAIL_ALREADY_EXIST = {
        "error_code": "organization-5",
        "error_message": "company email already exist",
    }
    COMPANY_MOBILE_ALREADY_EXIST = {
        "error_code": "organization-6",
        "error_message": "company mobile already exist",
    }
    YOU_ARE_NOT_A_MEMBER_OF_THIS_COMPANY = {
        "error_code": "organization-7",
        "error_message": "you are not a member of this company",
    }
    USER_ADDED_TO_COMPANY = {
        "error_code": "organization-8",
        "error_message": "user added to company",
    }
    USER_ALREADY_ADDED_TO_ORGANIZATION = {
        "error_code": "organization-9",
        "error_message": "user already added to organization",
    }
    CAN_NOT_CREATE_DEPARTMENT_WITHOUT_ORGANIZATION = {
        "error_code": "organization-10",
        "error_message": "can not create department without organization",
    }
    DEPARTMENT_ALREADY_EXIST = {
        "error_code": "organization-11",
        "error_message": "department already exist",
    }
    DEPARTMENT_NOT_FOUND = {
        "error_code": "organization-12",
        "error_message": "department not found",
    }
    TIME_NOT_AVAILABLE = {
        "error_code": "organization-13",
        "error_message": "time not available",
    }
    # Report
    THE_POST_AUTHOR_IS_UNABLE_TO_INCLUDE_A_REPORT = {
        "error_code": "report-1",
        "error_message": "the post author is unable to include a report.",
    }
    # Post
    IT_IS_NOT_AUTHORIZED_FOR_YOU_TO_REMOVE_THE_POST = {
        "error_code": "post-1",
        "error_message": "it is not authorized for you to remove the post.",
    }
