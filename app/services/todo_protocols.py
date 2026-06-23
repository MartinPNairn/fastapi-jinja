from typing import Protocol

from app.schemas.todo import TodoRequest
from app.models.todo import Todo
from app.models.user import User


class TodoReadServiceProtocol(Protocol):
    def get_by_id(self, todo_id: int, owner: User) -> Todo : ...

    def get_all_for_owner(self, owner: User) -> list[Todo]: ...


class TodoWriteServiceProtocol(Protocol):
    def create(self, todo_data: TodoRequest, owner: User) -> Todo: ...

    def update(self, todo_data: TodoRequest, todo_id: int, owner: User) -> Todo: ...

    def delete_for_owner(self, todo_id: int, owner: User) -> bool: ...


class TodoAdminServiceProtocol(Protocol):
    def get_all(self) -> list[Todo]: ...

    def delete(self, todo_id: int) -> bool: ...
    