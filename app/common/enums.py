from enum import Enum
from typing import Collection


class BaseEnum(Enum):
    def __str__(self):
        return self.value

    @classmethod
    def list(cls):
        return [attr.value for attr in cls]
        # return list(map(lambda c: c.value, cls))

    @classmethod
    def set(cls):
        return {attr.value for attr in cls}
        # return list(map(lambda c: c.value, cls))

    @classmethod
    def validate_item(cls, item):
        return item in cls.list()

    @classmethod
    def validate_items(cls, items: Collection):
        return cls.set() & set(items) == len(items)


class LoggingLevel(str, BaseEnum):
    CRITICAL = "CRITICAL"
    FATAL = "FATAL"
    ERROR = "ERROR"
    WARN = "WARN"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"
    NOTSET = "NOTSET"



class GoogleCalendarEventTypes(str, BaseEnum):
    DEFAULT = "default"
    FOCUS_TIME = "focusTime"
    OUT_OF_OFFICE = "outOfOffice"
    WORKING_LOCATION = "workingLocation"

class GoogleCalendarOrderByTypes(str, BaseEnum):
    START_TIME = "startTime"
    UPDATED = "updated"


class GoogleSheetValueInputOption(str, BaseEnum):
    RAW = "RAW"
    USER_ENTERED = "USER_ENTERED"


class GoogleSheetInsertDataOption(str, BaseEnum):
    OVERWRITE = "OVERWRITE"
    INSERT_ROWS = "INSERT_ROWS"


class GoogleSheetValueRenderOption(str, BaseEnum):
    FORMATTED_VALUE = "FORMATTED_VALUE"
    UNFORMATTED_VALUE = "UNFORMATTED_VALUE"
    FORMULA = "FORMULA"


class GoogleSheetDateTimeRenderOption(str, BaseEnum):
    SERIAL_NUMBER = "SERIAL_NUMBER"
    FORMATTED_STRING = "FORMATTED_STRING"
