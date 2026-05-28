from typing import Annotated, Protocol

from fastapi import Depends
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from app.api.dependencies import SessionDep
from app.models import Todo


class DatabaseError(Exception):
    pass


class TodoWriter(Protocol):
    def create_todo(self, todo_data: dict, owner_id: int) -> Todo: ...

    def update_todo(self, todo_data: dict, todo_id: int, owner_id: int) -> Todo | None: ...

    def delete_todo(self, todo_id: int) -> bool: ...

    def delete_todo_for_owner(self, todo_id: int, owner_id: int) -> bool: ...


class TodoReader(Protocol):

    def get_all_todos(self) -> list[Todo]: ...

    def get_all_todos_for_owner(self, owner_id: int) -> list[Todo]: ...

    def get_todo_by_id(self, todo_id: int, owner_id: int) -> Todo | None: ...


class TodoRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_todo(self, todo_data: dict, owner_id: int) -> Todo:
        try:
            new_todo = Todo(**todo_data, owner_id=owner_id)
            self.db.add(new_todo)
            self.db.commit()
            self.db.refresh(new_todo)
            return new_todo
        except IntegrityError as e:
            self.db.rollback()
            raise DatabaseError("Integrity constraint failed") from e
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError("Failed to create todo") from e

    def get_all_todos_for_owner(self, owner_id: int) -> list[Todo]:
        try:
            stmt = (
                select(Todo)
                .where(Todo.owner_id == owner_id)
            )
            return list(self.db.execute(stmt).scalars().all())
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to retrieve todos") from e

    def get_all_todos(self) -> list[Todo]:
        try:
            return list(self.db.execute(select(Todo)).scalars().all())
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to retrieve todos") from e
        

    def get_todo_by_id(self, todo_id: int, owner_id: int) -> Todo | None:
        try:
            stmt = (
                select(Todo)
                .where(Todo.id == todo_id, Todo.owner_id == owner_id)
            )
            return self.db.execute(stmt).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to retrieve todo") from e

    def update_todo(self, todo_data: dict, todo_id: int, owner_id: int) -> Todo | None:
        try:
            stmt = (
                update(Todo)
                .where(Todo.id == todo_id, Todo.owner_id == owner_id)
                .values(**todo_data)
                .returning(Todo)
            )
            result = self.db.execute(stmt)
            todo = result.scalar_one_or_none()
            if todo is None:
                return None
            self.db.commit()
            return todo
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError("Failed to update todo") from e

    def delete_todo(self, todo_id: int) -> bool:
        try:
            stmt = (
                delete(Todo)
                .where(Todo.id == todo_id)
            )
            result = self.db.execute(stmt)
            self.db.commit()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError("Failed to delete todo") from e
        

    def delete_todo_for_owner(self, todo_id: int, owner_id: int) -> bool:
        try:
            stmt = (
                delete(Todo)
                .where(Todo.id == todo_id, Todo.owner_id == owner_id)
            )
            result = self.db.execute(stmt)
            self.db.commit()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseError("Failed to delete todo") from e


def get_todo_repository(db: SessionDep) -> TodoRepository:
    return TodoRepository(db)


TodoReaderRepoDep = Annotated[TodoReader, Depends(get_todo_repository)]
TodoWriterRepoDep = Annotated[TodoWriter, Depends(get_todo_repository)]
