from typing import Annotated

from fastapi import Request, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates


from app.db.session import SessionLocal
from app.crud import get_entry
from app.models import User
from app.schemas.auth import LoginCredentials
from app.repositories.todo_repository import SQLAlchemyTodoRepository
from app.repositories.user_repository import SQLAlchemyUserRepository
from app.services.todo_service import TodoService
from app.services.user_service import UserService
from app.services.todo_protocols import (
    TodoReadService,
    TodoWriteService,
    TodoAdminService,
)
from app.services.user_protocols import (
    UserReadService,
    UserWriteService,
    UserAdminService,
)
from app.core.security.password_hasher import PwdlibPasswordHasher
from app.core.security.token_manager import verify_token, HTTPValidationException


templates = Jinja2Templates(directory="app/frontend/templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", refreshUrl="/auth/refresh")


def get_session():
    with SessionLocal() as session:
        yield session


def get_login_credentials(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> LoginCredentials:
    return LoginCredentials(
        username=request_form.username, password=request_form.password
    )


SessionDep = Annotated[Session, Depends(get_session)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]
FormDep = Annotated[LoginCredentials, Depends(get_login_credentials)]


def get_todo_repository(session: SessionDep) -> SQLAlchemyTodoRepository:
    return SQLAlchemyTodoRepository(session)


SQLAlchemyTodoRepositoryDep = Annotated[
    SQLAlchemyTodoRepository, Depends(get_todo_repository)
]


def get_todo_service(
    repository: SQLAlchemyTodoRepositoryDep,
    session: SessionDep,
) -> TodoService:
    return TodoService(repository, session)


TodoReadServiceDep = Annotated[TodoReadService, Depends(get_todo_service)]
TodoWriteServiceDep = Annotated[TodoWriteService, Depends(get_todo_service)]
TodoAdminServiceDep = Annotated[TodoAdminService, Depends(get_todo_service)]


def get_user_repository(session: SessionDep) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(session)


def get_password_hasher() -> PwdlibPasswordHasher:
    return PwdlibPasswordHasher()


SQLAlchemyUserRepositoryDep = Annotated[
    SQLAlchemyUserRepository, Depends(get_user_repository)
]
PwdlibPasswordHasherDep = Annotated[PwdlibPasswordHasher, Depends(get_password_hasher)]


def get_user_service(
    repository: SQLAlchemyUserRepositoryDep,
    hasher: PwdlibPasswordHasherDep,
    session: SessionDep,
) -> UserService:
    return UserService(repository, hasher, session)


UserReadServiceDep = Annotated[UserReadService, Depends(get_user_service)]
UserWriteServiceDep = Annotated[UserWriteService, Depends(get_user_service)]
UserAdminServiceDep = Annotated[UserAdminService, Depends(get_user_service)]


async def get_current_user(token: TokenDep, session: SessionDep) -> User:
    username = verify_token(token, "access")
    user = get_entry(User, session, User.username == username)
    if not user:
        raise HTTPValidationException(status_code=401)
    return user


async def get_current_user_from_cookie(
    request: Request, session: SessionDep
) -> User | None:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        return None

    try:
        username = verify_token(refresh_token, "refresh")
        user = get_entry(User, session, User.username == username)
        return user

    except HTTPValidationException:
        return None


CurrentUserDep = Annotated[User, Depends(get_current_user)]
CookieCurrentUserDep = Annotated[User | None, Depends(get_current_user_from_cookie)]
