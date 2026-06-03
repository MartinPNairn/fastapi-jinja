from typing import Protocol

from sqlalchemy.orm import Session

from app.models.todo import Todo
from app.repositories.todo_repository import TodoRepository


# class TodoWriter(Protocol):
#     def create_todo(self, todo_data: dict, owner_id: int) -> Todo: ...

#     def update_todo(self, todo_data: dict, todo_id: int, owner_id: int) -> Todo | None: ...

#     def delete_todo(self, todo_id: int) -> bool: ...

#     def delete_todo_for_owner(self, todo_id: int, owner_id: int) -> bool: ...


# class TodoReader(Protocol):
#     def get_all_todos(self) -> list[Todo]: ...

#     def get_all_todos_for_owner(self, owner_id: int) -> list[Todo]: ...

#     def get_todo_by_id(self, todo_id: int, owner_id: int) -> Todo | None: ...


class TodoService:
    def __init__(self, todo_repository: TodoRepository, session: Session) -> None:
        self._repository = todo_repository
        self._session = session

    