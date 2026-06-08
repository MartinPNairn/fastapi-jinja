from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from app.models import Todo


class SQLAlchemyTodoRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_all_for_owner(self, owner_id: int) -> list[Todo]:
        stmt = select(Todo).where(Todo.owner_id == owner_id)
        return list(self._session.execute(stmt).scalars().all())

    def get_all(self) -> list[Todo]:
        return list(self._session.execute(select(Todo)).scalars().all())

    def get_by_id(self, todo_id: int, owner_id: int) -> Todo | None:
        stmt = select(Todo).where(Todo.id == todo_id, Todo.owner_id == owner_id)
        return self._session.execute(stmt).scalar_one_or_none()

    def create(self, todo_data: dict, owner_id: int) -> Todo:
        new_todo = Todo(**todo_data, owner_id=owner_id)
        self._session.add(new_todo)
        return new_todo

    def update(self, todo_data: dict, todo_id: int, owner_id: int) -> Todo | None:
        stmt = (
            update(Todo)
            .where(Todo.id == todo_id, Todo.owner_id == owner_id)
            .values(**todo_data)
            .returning(Todo)
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def delete(self, todo_id: int) -> bool:
        stmt = delete(Todo).where(Todo.id == todo_id)
        result = self._session.execute(stmt)
        return result.rowcount > 0

    def delete_for_owner(self, todo_id: int, owner_id: int) -> bool:
        stmt = delete(Todo).where(Todo.id == todo_id, Todo.owner_id == owner_id)
        result = self._session.execute(stmt)
        return result.rowcount > 0
