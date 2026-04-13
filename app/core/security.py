from datetime import timedelta, datetime, UTC
import os
from typing import Any, Dict
from typing_extensions import Annotated, Doc

from sqlalchemy.orm import Session
from fastapi import HTTPException
from pwdlib import PasswordHash
import jwt
from dotenv import load_dotenv

from app.crud import get_entry
from app.models import User
from app.schemas.auth import Token


load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY") or "secret-key"
HASHING_ALGORITHM = os.getenv("HASHING_ALGORITHM") or "HS256"

password_hasher = PasswordHash.recommended()


class InvalidCredentialsException(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=401, detail="Could not validate credentials!")


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


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    payload = data.copy()
    expiring_time = datetime.now(UTC) + (
        expires_delta if expires_delta else timedelta(minutes=15)
    )
    payload.update({"exp": expiring_time})
    token_string = jwt.encode(
        payload=payload, key=SECRET_KEY, algorithm=HASHING_ALGORITHM
    )
    return token_string


def verify_token(token: str) -> str:
    try:
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[HASHING_ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise InvalidCredentialsException
        return username
    except jwt.InvalidTokenError:
        raise InvalidCredentialsException
    
