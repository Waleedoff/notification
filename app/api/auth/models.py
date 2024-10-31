
import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from app.common.generate_random_id_uuid import generate_random_id
from app.db.db import Base, Defaults


class User(Base, Defaults):
    __override_tablename__ = "auth_user"
    url_id: Mapped[str] = sa.Column(sa.String, nullable=False, index=True, unique=True, default=generate_random_id)
    username: Mapped[str] = sa.Column(sa.String, nullable=False)
    full_name: Mapped[str] = sa.Column(sa.String, nullable=False)
    email: Mapped[str] = sa.Column(sa.String, nullable=False)
    hashed_password: Mapped[str] = sa.Column(sa.String, nullable=False)
    disabled: Mapped[bool] = sa.Column(sa.Boolean, default=False)
