from datetime import timedelta, datetime, UTC

import jwt

from app.core.config import Settings
from app.exceptions.auth_exceptions import (
    TokenSubjectMissingError,
    WrongTokenTypeError,
    ExpiredTokenError,
    InvalidTokenError,
)
from app.core.security.security_protocols import TokenServiceProtocol


class TokenService(TokenServiceProtocol):
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
                raise TokenSubjectMissingError()
            if token_type != expected_type:
                raise WrongTokenTypeError()
            return username

        except jwt.ExpiredSignatureError:
            raise ExpiredTokenError()

        except jwt.InvalidTokenError:
            raise InvalidTokenError()
