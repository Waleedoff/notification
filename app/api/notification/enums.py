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


class Status(str, BaseEnum):
    PUBLISHED = "PUBLISHED"
    DELETED = "DELETED"
    DRAFT = "DRAFT"
    
    

class NotificationType(str, BaseEnum):
    NORMAL = "NORMAL"

class NotificationStatus(str, BaseEnum):
    SENT = "SENT"
    STORED_ONLY = "STORED_ONLY"
