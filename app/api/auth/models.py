
from typing import TYPE_CHECKING
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, relationship

from app.common.generate_random_id_uuid import generate_random_id
from app.db.db import Base, Defaults


if TYPE_CHECKING:
    from app.api.notification.models import Device, Notification
    

class User(Base, Defaults):
    url_id: Mapped[str] = sa.Column(sa.String, nullable=False, index=True, unique=True, default=generate_random_id)
    username: Mapped[str] = sa.Column(sa.String, nullable=False)
    full_name: Mapped[str] = sa.Column(sa.String, nullable=False)
    email: Mapped[str] = sa.Column(sa.String, nullable=False)
    hashed_password: Mapped[str] = sa.Column(sa.String, nullable=False)
    disabled: Mapped[bool] = sa.Column(sa.Boolean, default=False)
    
    devices: Mapped[list["Device"]] = relationship(
        "Device", back_populates="user", cascade="all, delete-orphan"
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
