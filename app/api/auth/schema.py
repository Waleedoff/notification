from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    full_name: str
    username: str
    password: str | None = None
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserResponse(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(UserResponse):
    hashed_password: str
