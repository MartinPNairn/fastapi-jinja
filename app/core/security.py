import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import jwt
from app.crud import get_entry
from app.models import User

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
HASHING_ALGORITHM = os.getenv("HASHING_ALGORITHM")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_password_hash(raw_password: str) -> str:
    return bcrypt_context.hash(secret=raw_password)


def verify_password_hash(raw_password: str, password_hash: str) -> bool:
    return bcrypt_context.verify(raw_password, password_hash)


def authenticate_user(username: str, password: str, db: Session) -> User | bool:
    user = get_entry(User, db, User.username == username)
    if not user:
        print("User to authenticate has not been found.")
        return False
    if not verify_password_hash(password, user.hashed_password):
        print("User authentication has not been succesfull.")
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expiring_time = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expiring_time})
    encoded_jwt = jwt.encode(payload=to_encode, key=SECRET_KEY, algorithm=HASHING_ALGORITHM)
    return encoded_jwt
