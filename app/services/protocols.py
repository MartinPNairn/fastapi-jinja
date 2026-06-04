from typing import Protocol

from app.models.todo import Todo


class TodoReadService(Protocol):
    def get_by_id(self, todo_id: int, owner_id: int) -> Todo | None: ...

    def get_all_for_owner(self, owner_id: int) -> list[Todo]: ...


class TodoWriteService(Protocol):
    def create(self, todo_data: dict, owner_id: int) -> Todo: ...

    def update(self, todo_data: dict, todo_id: int, owner_id: int) -> Todo | None: ...

    def delete_for_owner(self, todo_id: int, owner_id: int) -> bool: ...


class TodoAdminService(Protocol):
    def get_all(self) -> list[Todo]: ...

    def delete(self, todo_id: int) -> bool: ...
    