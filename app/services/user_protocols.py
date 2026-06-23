from typing import Protocol

from app.schemas.users import ChangePasswordRequest, ChangePhoneRequest
from app.schemas.auth import UserCreateRequest, LoginCredentials
from app.models.user import User


class UserReadServiceProtocol(Protocol):
    def authenticate(self, form_data: LoginCredentials) -> User: ...

    def get_by_username(self, username: str) -> User: ...

    def get_by_id(self, user_id: int) -> User: ...


class UserWriteServiceProtocol(Protocol):
    def register(self, user_data: UserCreateRequest) -> User: ...

    def change_password(self, user: User, pass_data: ChangePasswordRequest) -> None: ...

    def change_phone(self, user: User, phone_data: ChangePhoneRequest) -> None: ...


class UserAdminServiceProtocol(Protocol):
    def get_all(self) -> list[User]: ...

    def delete(self, user_id: int) -> bool: ...


class UserServiceProtocol(UserReadServiceProtocol, UserWriteServiceProtocol, UserAdminServiceProtocol, Protocol): ...
