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
    def create(self, todo_data: dict, owner_id: int) -> Todo: ...

    def update(self, todo_data: dict, todo_id: int, owner_id: int) -> Todo | None: ...

    def delete(self, todo_id: int) -> bool: ...

    def delete_for_owner(self, todo_id: int, owner_id: int) -> bool: ...


class TodoReader(Protocol):
    def get_all(self) -> list[Todo]: ...

    def get_all_for_owner(self, owner_id: int) -> list[Todo]: ...

    def get_by_id(self, todo_id: int, owner_id: int) -> Todo | None: ...


class TodoRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, todo_data: dict, owner_id: int) -> Todo:
        try:
            new_todo = Todo(**todo_data, owner_id=owner_id)
            self._session.add(new_todo)
            self._session.commit()
            self._session.refresh(new_todo)
            return new_todo
        except IntegrityError as e:
            self._session.rollback()
            raise DatabaseError("Integrity constraint failed") from e
        except SQLAlchemyError as e:
            self._session.rollback()
            raise DatabaseError("Failed to create todo") from e

    def get_all_for_owner(self, owner_id: int) -> list[Todo]:
        try:
            stmt = select(Todo).where(Todo.owner_id == owner_id)
            return list(self._session.execute(stmt).scalars().all())
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to retrieve todos") from e

    def get_all(self) -> list[Todo]:
        try:
            return list(self._session.execute(select(Todo)).scalars().all())
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to retrieve todos") from e

    def get_by_id(self, todo_id: int, owner_id: int) -> Todo | None:
        try:
            stmt = (
                select(Todo)
                .where(Todo.id == todo_id, Todo.owner_id == owner_id)
            )
            return self._session.execute(stmt).scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError("Failed to retrieve todo") from e

    def update(self, todo_data: dict, todo_id: int, owner_id: int) -> Todo | None:
        try:
            stmt = (
                update(Todo)
                .where(Todo.id == todo_id, Todo.owner_id == owner_id)
                .values(**todo_data)
                .returning(Todo)
            )
            result = self._session.execute(stmt)

            todo = result.scalar_one_or_none()
            if todo is None:
                # self.session.rollback()
                return None
            
            self._session.commit()
            return todo
        except SQLAlchemyError as e:
            self._session.rollback()
            raise DatabaseError("Failed to update todo") from e

    def delete(self, todo_id: int) -> bool:
        try:
            stmt = delete(Todo).where(Todo.id == todo_id)
            result = self._session.execute(stmt)

            deleted = result.rowcount > 0
            if not deleted:
                # self.session.rollback()
                return False
            
            self._session.commit()
            return True
        except SQLAlchemyError as e:
            self._session.rollback()
            raise DatabaseError("Failed to delete todo") from e

    def delete_for_owner(self, todo_id: int, owner_id: int) -> bool:
        try:
            stmt = delete(Todo).where(Todo.id == todo_id, Todo.owner_id == owner_id)
            result = self._session.execute(stmt)

            deleted = result.rowcount > 0
            if not deleted:
                # self.session.rollback()
                return False
            
            self._session.commit()
            return True
        except SQLAlchemyError as e:
            self._session.rollback()
            raise DatabaseError("Failed to delete todo") from e


def get_todo_repository(session: SessionDep) -> TodoRepository:
    return TodoRepository(session)


TodoReaderRepoDep = Annotated[TodoReader, Depends(get_todo_repository)]
TodoWriterRepoDep = Annotated[TodoWriter, Depends(get_todo_repository)]
