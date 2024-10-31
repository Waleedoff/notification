
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.auth.models import User
from app.api.auth.schema import CreateUserRequest
from app.api.auth.services.authSetup import get_password_hash


def user_register_(
    body: CreateUserRequest,
    session: Session,

):
    stmt = select(User).where(User.email == body.email)
    user_email: User | None = session.execute(stmt).scalar_one_or_none()
    if user_email is not None:
        raise HTTPException(status_code=400, detail="Email already registered")
    password = body.password
    hash_password = get_password_hash(password)

    user = User(**body.model_dump(exclude={"password"}), hashed_password=hash_password, created_by="system")
    session.add(user)
    
    return {"message": "User created successfully"}
