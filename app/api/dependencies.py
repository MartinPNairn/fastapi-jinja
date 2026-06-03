from typing import Annotated

from fastapi import Request, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates


from app.db.session import SessionLocal
from app.crud import get_entry
from app.models import User
from app.core.security import verify_token, InvalidCredentialsException


templates = Jinja2Templates(directory="app/frontend/templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", refreshUrl="/auth/refresh")


def get_session():
    with SessionLocal() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]
FormDep = Annotated[OAuth2PasswordRequestForm, Depends()]


async def get_current_user(token: TokenDep, session: SessionDep) -> User:
    username = verify_token(token, "access")
    user = get_entry(User, session, User.username == username)
    if not user:
        raise InvalidCredentialsException()
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


async def get_current_user_from_cookie(request: Request, session: SessionDep) -> User | None:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        return None

    try:
        username = verify_token(refresh_token, "refresh")
        user = get_entry(User, session, User.username == username)
        return user
    except InvalidCredentialsException:
        return None


CookieCurrentUserDep = Annotated[User | None, Depends(get_current_user_from_cookie)]
