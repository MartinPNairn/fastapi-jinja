from fastapi import APIRouter, Response, HTTPException

from app.api.dependencies import (
    CredentialsFormDep,
    UserReadServiceDep,
    AuthServiceDep,
    CookieCurrentUserDep,
)
from app.schemas import Token
from app.core.config import SettingsDep
from app.exceptions.user_exceptions import (
    UserNotFoundError,
    UserServiceError,
    InvalidCredentialsError,
)
from app.exceptions.http_exceptions import HTTPValidationException


router = APIRouter()


@router.post("/login")
async def login_for_access_and_refresh_token(
    response: Response,
    credentials_data: CredentialsFormDep,
    settings: SettingsDep,
    user_service: UserReadServiceDep,
    auth_service: AuthServiceDep,
) -> Token:
    user = user_service.authenticate(credentials_data)
    access_token = auth_service.issue_access_token(user)
    refresh_token = auth_service.issue_refresh_token(user)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        path="/",
        max_age=int(settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400),
    )

    return Token(access_token=access_token, token_type="bearer")


@router.post("/refresh")
def refresh_for_new_access_token(
    auth_service: AuthServiceDep,
    user: CookieCurrentUserDep,
) -> Token:
    if user is None:
        raise HTTPValidationException(
            status_code=401,
            detail="Missing refresh token",
        )
    new_access_token = auth_service.issue_access_token(user)
    return Token(access_token=new_access_token, token_type="bearer")


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    return {"detail": "Logged out"}
