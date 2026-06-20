from datetime import timedelta, datetime, UTC

import jwt

from app.core.config import Settings, get_settings
from app.exceptions.security_exceptions import HTTPValidationException


class TokenService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def create_access_token(
        self,
        data: dict,
    ) -> str:
        expiration = self.settings.ACCESS_TOKEN_EXPIRE_MINUTES
        return self._create_jwt(
            data=data,
            token_type="access",
            expires_delta=timedelta(minutes=expiration),
        )

    def create_refresh_token(
        self,
        data: dict,
    ) -> str:
        expiration = self.settings.REFRESH_TOKEN_EXPIRE_DAYS
        return self._create_jwt(
            data=data,
            token_type="refresh",
            expires_delta=timedelta(days=expiration),
        )

    def _create_jwt(
        self,
        data: dict,
        token_type: str,
        expires_delta: timedelta,
    ) -> str:
        to_encode = data.copy()
        to_encode.update(
            {
                "exp": datetime.now(UTC) + expires_delta,
                "token_type": token_type,
            }
        )
        return jwt.encode(
            payload=to_encode,
            key=self.settings.SECRET_KEY,
            algorithm=self.settings.HASHING_ALGORITHM,
        )

    def verify_token(
        self,
        token: str,
        expected_type: str,
    ) -> str:
        try:
            payload = jwt.decode(
                jwt=token,
                key=self.settings.SECRET_KEY,
                algorithms=[self.settings.HASHING_ALGORITHM],
            )
            username = payload.get("sub")
            token_type = payload.get("token_type")

            if not username:
                raise HTTPValidationException(
                    status_code=401,
                    detail="Invalid token: Subject missing"
                )
            if token_type != expected_type:
                raise HTTPValidationException(
                    status_code=401,
                    detail="Invalid token type",
                )
            return username

        except jwt.ExpiredSignatureError:
            raise HTTPValidationException(
                status_code=401,
                detail="Token has expired",
            )

        except jwt.InvalidTokenError:
            raise HTTPValidationException(
                status_code=401,
                detail="Invalid Token",
            )


# ------------------------------------------------------


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
            raise HTTPValidationException(status_code=401)
        if token_type != expected_type:
            raise HTTPValidationException(status_code=401, detail="Invalid token type")
        return username

    except jwt.ExpiredSignatureError:
        raise HTTPValidationException(status_code=401, detail="Token has expired")

    except jwt.InvalidTokenError:
        raise HTTPValidationException(status_code=401, detail="Invalid Token")
