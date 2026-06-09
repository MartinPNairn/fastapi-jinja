from datetime import timedelta, datetime, UTC

import jwt

from app.core.config import get_settings
from app.exceptions.security_exceptions import InvalidCredentialsException


def create_access_token(data: dict, expiration_time_minutes: float = 15) -> str:
    expiration_delta = timedelta(minutes=expiration_time_minutes)
    return create_jwt_token(
        data=data,
        token_type="access",
        expires_delta=expiration_delta,
    )  # type: ignore


def create_refresh_token(data: dict, expiration_time_days: float = 7) -> str:
    expiration_delta = timedelta(days=expiration_time_days)
    return create_jwt_token(
        data=data,
        token_type="refresh",
        expires_delta=expiration_delta,
    )  # type: ignore


def create_jwt_token(data: dict, token_type: str, expires_delta: timedelta) -> str:
    settings = get_settings()
    to_encode = data.copy()
    expiring_time = datetime.now(UTC) + expires_delta
    to_encode.update(
        {
            "exp": expiring_time,
            "token_type": token_type,
        }
    )
    return jwt.encode(
        payload=to_encode, key=settings.SECRET_KEY, algorithm=settings.HASHING_ALGORITHM
    )


def verify_token(token: str, expected_type: str) -> str:
    try:
        settings = get_settings()
        payload = jwt.decode(
            jwt=token, key=settings.SECRET_KEY, algorithms=[settings.HASHING_ALGORITHM]
        )
        username = payload.get("sub")
        token_type = payload.get("token_type")

        if not username:
            raise InvalidCredentialsException()
        if token_type != expected_type:
            raise InvalidCredentialsException(detail="Invalid token type")
        return username

    except jwt.ExpiredSignatureError:
        raise InvalidCredentialsException(detail="Token has expired")

    except jwt.InvalidTokenError:
        raise InvalidCredentialsException(detail="Invalid Token")