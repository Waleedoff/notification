from datetime import timedelta

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.auth.services.authSetup import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token


def user_login_(form_data: OAuth2PasswordRequestForm, session: Session):
        user = authenticate_user(form_data.username, form_data.password, session=session)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
