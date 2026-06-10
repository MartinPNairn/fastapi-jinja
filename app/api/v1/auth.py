from fastapi import APIRouter, Response, Request, HTTPException

from app.api.dependencies import SessionDep, FormDep, UserReadServiceDep
from app.schemas import Token
from app.crud import get_entry
from app.models import User
from app.core.config import SettingsDep
from app.exceptions.user_exceptions import (
    UserNotFoundError,
    UserServiceError,
    InvalidCredentialsError,
)
from app.exceptions.security_exceptions import HTTPValidationException
from app.core.security.password_hasher import authenticate_user
from app.core.security.token_manager import (
    create_access_token,
    create_refresh_token,
    verify_token,
)


router = APIRouter()


# Login and generate JWT token for user
@router.post("/login", response_model=Token)
async def login_for_access_and_refresh_token(
    response: Response,
    credentials_data: FormDep,
    settings: SettingsDep,
    user_service: UserReadServiceDep,
) -> Token:
    try:
        user = user_service.authenticate(credentials_data)

        access_token = create_access_token(
            data={"sub": user.username, "id": user.id, "role": user.role},
            expiration_time_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )

        refresh_token = create_refresh_token(
            data={"sub": user.username},
            expiration_time_days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=settings.ENVIRONMENT != "development",
            path="/",
            max_age=int(settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400),
        )

        return Token(access_token=access_token, token_type="bearer")

    except UserNotFoundError as e:
        raise HTTPValidationException(
            status_code=404,
            detail="User not found.",
        ) from e

    except InvalidCredentialsError as e:
        raise HTTPValidationException(
            status_code=401,
            detail="Invalid credentials.",
        ) from e

    except UserServiceError as e:
        raise HTTPException(
            status_code=500,
            detail="Database error.",
        ) from e


@router.post("/refresh", response_model=Token)
def refresh_for_new_access_token(
    request: Request,
    session: SessionDep,
    settings: SettingsDep,
) -> Token:
    refresh_token = request.cookies.get("refresh_token")

    if refresh_token is None:
        raise HTTPValidationException(detail="Missing refresh token")

    username = verify_token(refresh_token, "refresh")
    user = get_entry(User, session, User.username == username)
    if user is None:
        raise HTTPValidationException(status_code=401, detail="User not found")

    new_access_token = create_access_token(
        data={"sub": user.username, "id": user.id, "role": user.role},
        expiration_time_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    return Token(access_token=new_access_token, token_type="bearer")


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    return {"detail": "Logged out"}
