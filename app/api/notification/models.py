import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, relationship

from app.common.enums import NotificationType
from app.api.auth.models import User
from app.common.enums import Status
from app.db.db import Base, Defaults



class Device(Base, Defaults):
    user_id: Mapped[str] = sa.Column(sa.ForeignKey("users.id"), nullable=False)
    device_token: Mapped[str] = sa.Column(sa.String, nullable=False, unique=True)
    device_type: Mapped[str] = sa.Column(sa.String, nullable=False)
    is_active: Mapped[bool] = sa.Column(sa.Boolean, nullable=False, default=True)
    status: Mapped[str] = sa.Column(sa.String, default=Status.PUBLISHED, nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="devices")


class Notification(Base, Defaults):
    notification_id: Mapped[str] = sa.Column(
        sa.String, nullable=False, index=True, unique=True
    )
    user_id: Mapped[str] = sa.Column(sa.ForeignKey("users.id"), nullable=False)
    device_id: Mapped[str | None] = sa.Column(
        sa.ForeignKey("devices.id"), nullable=True
    )
    title: Mapped[str] = sa.Column(sa.String, nullable=False)
    body: Mapped[str] = sa.Column(sa.String, nullable=False)
    image: Mapped[str | None] = sa.Column(sa.String, nullable=True)
    data: Mapped[dict] = sa.Column(JSONB, nullable=True)
    is_read: Mapped[bool] = sa.Column(sa.Boolean, nullable=False, default=False)
    notification_status: Mapped[str] = sa.Column(sa.String, nullable=False)
    notification_type: Mapped[str] = sa.Column(
        sa.String, nullable=False, default=NotificationType.NORMAL
    )
    status: Mapped[str] = sa.Column(sa.String, default=Status.PUBLISHED, nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="notifications")
    device: Mapped["Device"] = relationship("Device")

