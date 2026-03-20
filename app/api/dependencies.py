from typing import Annotated
import os
from dotenv import load_dotenv

import jwt
from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates


from app.db.session import SessionLocal
from app.crud import get_entry
from app.models import User

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
HASHING_ALGORITHM = os.getenv("HASHING_ALGORITHM")

#
templates = Jinja2Templates(directory="app/frontend/templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_db():
    with SessionLocal() as db:
        yield db


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]
FormDep = Annotated[OAuth2PasswordRequestForm, Depends()]


async def get_current_user(token: TokenDep, db: SessionDep) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials. Bloody hell, mate!",
    )
    try:
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[HASHING_ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if not username or not user_id:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    user = get_entry(User, db, User.username == username)
    if not user:
        raise credentials_exception
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
