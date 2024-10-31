from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.auth.schema import CreateUserRequest, Token, UserResponse
from app.api.auth.services.authSetup import (
    get_current_active_user,
)
from app.api.auth.services.user_login import user_login_
from app.api.auth.services.user_register import user_register_
from app.dependencies import db_session

router = APIRouter()

prefix = "/auth"
tags = ["auth"]


@router.post("/register",)
async def user_register(body: CreateUserRequest, session: Session = db_session):
    return user_register_(body=body, session=session)


@router.post("/login",)
def user_login(form_data: OAuth2PasswordRequestForm = Depends(), session:Session = db_session)->Token:

    return user_login_(form_data = form_data, session=session)


@router.get("/user/me/", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_active_user)):
    return current_user


@router.get("/user/me/items")
async def read_own_items(current_user: UserResponse = Depends(get_current_active_user)):
    return [{"item_id": 1, "owner": current_user}]
