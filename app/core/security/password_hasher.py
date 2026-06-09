from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.crud import get_entry
from app.models import User
from app.schemas import HashedPassword


password_hasher = PasswordHash.recommended()


def create_password_hash(raw_password: str) -> str:
    return password_hasher.hash(raw_password)


def authenticate_user(username: str, password: str, session: Session) -> bool | User:
    user = get_entry(User, session, User.username == username.lower())
    if user is None:
        return False
    if not verify_password_hash(password, user.hashed_password):
        return False
    return user


def verify_password_hash(raw_password: str, hashed_password: str) -> bool:
    return password_hasher.verify(raw_password, hashed_password)


class PwdlibPasswordHasher:
    def __init__(self) -> None:
        self._hasher = PasswordHash.recommended()

    def hash(self, raw_password: str) -> HashedPassword:
        hashed_pass = self._hasher.hash(raw_password)
        return HashedPassword(hashed_password=hashed_pass)


    def verify(self, raw_password: str, hashed_password: str) -> bool: 
        return self._hasher.verify(raw_password, hashed_password)
