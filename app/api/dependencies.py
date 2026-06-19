from typing import Annotated

from fastapi import Request, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
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
from app.core.security.token_manager import verify_token
from app.exceptions.security_exceptions import HTTPValidationException
from app.exceptions.user_exceptions import UserNotFoundError, UserServiceError


templates = Jinja2Templates(directory="app/frontend/templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", refreshUrl="/auth/refresh")


def get_session():
    with SessionLocal() as session:
        yield session


def get_login_credentials(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> LoginCredentials:
    return LoginCredentials(
        username=request_form.username,
        password=request_form.password,
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


async def get_current_user(
    token: TokenDep,
    user_service: UserReadServiceDep,
) -> User:
    username = verify_token(token, "access")
    try:
        return user_service.get_by_username(username)

    except UserNotFoundError:
        raise HTTPValidationException(
            status_code=401,
            detail="Authorization failed."
        )

    except UserServiceError as e:
        raise HTTPException(
            status_code=500,
            detail="Database error.",
        ) from e


async def get_current_user_from_cookie(
    request: Request,
    user_service: UserReadServiceDep,
) -> User | None:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        return None

    try:
        username = verify_token(refresh_token, "refresh")
        return user_service.get_by_username(username)

    except (HTTPValidationException, UserNotFoundError):
        return None

    except UserServiceError as e:
        raise HTTPException(
            status_code=500,
            detail="Database error.",
        ) from e


CurrentUserDep = Annotated[User, Depends(get_current_user)]
CookieCurrentUserDep = Annotated[User | None, Depends(get_current_user_from_cookie)]


async def require_admin(user: CurrentUserDep):
    if user.role.casefold() != "admin":
        raise HTTPValidationException(
            status_code=403,
            detail="Admin access required"
        )
    return user


CurrentUserAdminDep = Annotated[User, Depends(require_admin)]