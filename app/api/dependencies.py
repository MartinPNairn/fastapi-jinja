from typing import Annotated

from fastapi import Request, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import User
from app.schemas.auth import LoginCredentials
from app.core.config import SettingsDep
from app.repositories.todo_repository import SQLAlchemyTodoRepository
from app.repositories.user_repository import SQLAlchemyUserRepository
from app.services.todo_service import TodoService
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.services.todo_protocols import (
    TodoReadServiceProtocol,
    TodoWriteServiceProtocol,
    TodoAdminServiceProtocol,
)
from app.services.user_protocols import (
    UserReadServiceProtocol,
    UserWriteServiceProtocol,
    UserAdminServiceProtocol,
)
from app.services.auth_protocols import AuthServiceProtocol
from app.core.security.security_protocols import (
    PasswordHasherProtocol,
    TokenServiceProtocol,
)
from app.core.security.password_hasher import PwdlibPasswordHasher
from app.core.security.token_service import TokenService
from app.exceptions.http_exceptions import HTTPValidationException
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


def get_token_service(settings: SettingsDep) -> TokenService:
    return TokenService(settings)


SessionDep = Annotated[Session, Depends(get_session)]
TokenServiceDep = Annotated[TokenServiceProtocol, Depends(get_token_service)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]
CredentialsFormDep = Annotated[LoginCredentials, Depends(get_login_credentials)]


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


TodoReadServiceDep = Annotated[TodoReadServiceProtocol, Depends(get_todo_service)]
TodoWriteServiceDep = Annotated[TodoWriteServiceProtocol, Depends(get_todo_service)]
TodoAdminServiceDep = Annotated[TodoAdminServiceProtocol, Depends(get_todo_service)]


def get_user_repository(session: SessionDep) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(session)


def get_password_hasher() -> PwdlibPasswordHasher:
    return PwdlibPasswordHasher()


SQLAlchemyUserRepositoryDep = Annotated[
    SQLAlchemyUserRepository, Depends(get_user_repository)
]
PwdlibPasswordHasherDep = Annotated[
    PasswordHasherProtocol, Depends(get_password_hasher)
]


def get_user_service(
    repository: SQLAlchemyUserRepositoryDep,
    hasher: PwdlibPasswordHasherDep,
    session: SessionDep,
) -> UserService:
    return UserService(repository, hasher, session)


UserReadServiceDep = Annotated[UserReadServiceProtocol, Depends(get_user_service)]
UserWriteServiceDep = Annotated[UserWriteServiceProtocol, Depends(get_user_service)]
UserAdminServiceDep = Annotated[UserAdminServiceProtocol, Depends(get_user_service)]


def get_auth_service(
    token_service: TokenServiceDep,
    user_service: UserReadServiceDep,
) -> AuthService:
    return AuthService(token_service, user_service)


AuthServiceDep = Annotated[AuthServiceProtocol, Depends(get_auth_service)]


async def get_current_user(
    token: TokenDep,
    token_service: TokenServiceDep,
    user_service: UserReadServiceDep,
) -> User:
    username = token_service.verify_token(token, "access")
    try:
        return user_service.get_by_username(username)

    except UserNotFoundError:
        raise HTTPValidationException(status_code=401, detail="Authorization failed.")

    except UserServiceError as e:
        raise HTTPException(
            status_code=500,
            detail="Database error.",
        ) from e


async def get_current_user_from_cookie(
    request: Request,
    token_service: TokenServiceDep,
    user_service: UserReadServiceDep,
) -> User | None:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        return None

    try:
        username = token_service.verify_token(refresh_token, "refresh")
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
        raise HTTPValidationException(status_code=403, detail="Admin access required")
    return user


CurrentUserAdminDep = Annotated[User, Depends(require_admin)]
