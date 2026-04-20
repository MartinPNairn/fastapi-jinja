from typing import Annotated
import os
from dotenv import load_dotenv

from fastapi import Request
from fastapi.params import Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates


from app.db.session import SessionLocal
from app.crud import get_entry
from app.models import User
from app.core.security import verify_token, InvalidCredentialsException

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
HASHING_ALGORITHM = os.getenv("HASHING_ALGORITHM")

templates = Jinja2Templates(directory="app/frontend/templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", refreshUrl="/auth/refresh")


def get_db():
    with SessionLocal() as db:
        yield db


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]
FormDep = Annotated[OAuth2PasswordRequestForm, Depends()]


async def get_current_user(token: TokenDep, db: SessionDep) -> User:
    username = verify_token(token, "access")
    user = get_entry(User, db, User.username == username)
    if not user:
        raise InvalidCredentialsException()
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


async def get_current_user_from_cookie(request: Request, db: SessionDep) -> User | None:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        return None

    try:
        username = verify_token(refresh_token, "refresh")
        user = get_entry(User, db, User.username == username)
        return user
    except InvalidCredentialsException:
        return None


CookieCurrentUserDep = Annotated[User | None, Depends(get_current_user_from_cookie)]
