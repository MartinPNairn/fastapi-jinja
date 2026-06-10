from typing import Protocol

from app.schemas.users import ChangePasswordRequest, ChangePhoneRequest
from app.schemas.auth import UserCreateRequest, LoginCredentials
from app.models.user import User


class UserReadService(Protocol):
    def get_by_id(self, user_id: int) -> User: ...

    def authenticate(self, form_data: LoginCredentials) -> User: ...


class UserWriteService(Protocol):
    def create_account(self, user_data: UserCreateRequest) -> User: ...

    def change_password(self, user: User, pass_data: ChangePasswordRequest) -> None: ...

    def change_phone(self, user: User, phone_data: ChangePhoneRequest) -> None: ...

    def _update(self, user: User, new_data: dict) -> None: ...


class UserAdminService(Protocol):
    def get_all(self) -> list[User]: ...

    def delete(self, user_id: int) -> bool: ...


class UserServiceProtocol(UserReadService, UserWriteService, UserAdminService, Protocol): ...
