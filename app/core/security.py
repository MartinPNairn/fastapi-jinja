from datetime import timedelta, datetime, UTC
import os

from sqlalchemy.orm import Session
from fastapi import HTTPException
from pwdlib import PasswordHash
import jwt
from dotenv import load_dotenv

from app.crud import get_entry
from app.models import User


load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY") or "secret-key"
HASHING_ALGORITHM = os.getenv("HASHING_ALGORITHM") or "HS256"

password_hasher = PasswordHash.recommended()


class InvalidCredentialsException(HTTPException):
    def __init__(self, detail: str = "Could not validate credentials!") -> None:
        super().__init__(
            status_code=401,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_password_hash(raw_password: str) -> str:
    return password_hasher.hash(raw_password)


def authenticate_user(username: str, password: str, db: Session) -> bool | User:
    user = get_entry(User, db, User.username == username.lower())
    if user is None:
        return False
    if not verify_password_hash(password, user.hashed_password):
        return False
    return user


def verify_password_hash(raw_password: str, hashed_password: str) -> bool:
    return password_hasher.verify(raw_password, hashed_password)


def create_access_token(data: dict, expiration_time_minutes: float = 15) -> str:
    expiration_delta = timedelta(minutes=expiration_time_minutes)
    return create_jwt_token(
        data=data,
        token_type="access",
        expires_delta=expiration_delta,
    )


def create_refresh_token(data: dict, expiration_time_days: float = 7) -> str:
    expiration_delta = timedelta(days=expiration_time_days)
    return create_jwt_token(
        data=data,
        token_type="refresh",
        expires_delta=expiration_delta,
    )


def create_jwt_token(data: dict, token_type: str, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expiring_time = datetime.now(UTC) + expires_delta
    to_encode.update(
        {
            "exp": expiring_time,
            "token_type": token_type,
        }
    )
    return jwt.encode(payload=to_encode, key=SECRET_KEY, algorithm=HASHING_ALGORITHM)


def verify_token(token: str, expected_type: str) -> str:
    try:
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[HASHING_ALGORITHM])
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
