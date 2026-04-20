import os
from dotenv import load_dotenv
from fastapi import APIRouter, Response, Request

from app.api.dependencies import SessionDep, FormDep
from app.schemas import Token
from app.crud import get_entry
from app.models import User
from app.core.security import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    verify_token,
    InvalidCredentialsException,
)


load_dotenv()
ENVIRONMENT = os.getenv("ENVIRONMENT") or "development"
ACCESS_TOKEN_EXPIRE_MINUTES = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES") or 15)
REFRESH_TOKEN_EXPIRE_DAYS = float(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS") or 7)

router = APIRouter()


# Login and generate JWT token for user
@router.post("/token", response_model=Token)
async def login_for_access_and_refresh_token(
    response: Response,
    form_data: FormDep,
    db: SessionDep,
) -> Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise InvalidCredentialsException()

    access_token = create_access_token(
        data={"sub": user.username, "id": user.id, "role": user.role},
        expiration_time_minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
    )

    refresh_token = create_refresh_token(
        data={"sub": user.username},
        expiration_time_days=REFRESH_TOKEN_EXPIRE_DAYS,
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=ENVIRONMENT != "development",
        path="/",
        max_age=int(REFRESH_TOKEN_EXPIRE_DAYS * 86400),
    )

    return Token(access_token=access_token, token_type="bearer")


@router.post("/refresh", response_model=Token)
def refresh_for_new_access_token(
    request: Request,
    db: SessionDep,
) -> Token:
    refresh_token = request.cookies.get("refresh_token")

    if refresh_token is None:
        raise InvalidCredentialsException(detail="Missing refresh token")

    username = verify_token(refresh_token, "refresh")
    user = get_entry(User, db, User.username == username)
    if user is None:
        raise InvalidCredentialsException(detail="User not found")

    new_access_token = create_access_token(
        data={"sub": user.username, "id": user.id, "role": user.role},
        expiration_time_minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    return Token(access_token=new_access_token, token_type="bearer")


# TODO: define /auth/logout endpoint
@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    return {"detail": "Logged out"}
