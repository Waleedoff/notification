from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.auth.models import User
from app.api.auth.schema import CreateUserRequest, TokenData, UserInDB
from app.dependencies import db_session

SECRET_KEY = "83daa0256a2289b0fb23693bf1f6034d44396675749244721a2b20e896e11662"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_user_(
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


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str, session: Session):
    stmt = select(User).where(User.username == username)

    user = session.execute(stmt).scalar_one_or_none()

    return user


def authenticate_user(username: str, password: str, session: Session):
    user = get_user(username=username, session=session)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False

    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



async def get_current_user(token: str = Depends(oauth2_scheme), session:Session = db_session):


    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                         detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception

        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception
    user = get_user(username=token_data.username, session=session)
    if user is None:
        raise credential_exception

    return user


async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):

    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user
