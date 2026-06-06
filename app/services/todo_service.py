from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.models.todo import Todo
from app.models.user import User
from app.schemas.todo import TodoRequest
from app.repositories.todo_repository import TodoRepository
from app.exceptions.todo_exceptions import (
    TodoAlreadyExistsError,
    TodoNotFoundError,
    TodoServiceError,
)


class TodoService:
    def __init__(self, repository: TodoRepository, session: Session) -> None:
        self._repository = repository
        self._session = session

    def get_by_id(
        self,
        todo_id: int,
        owner: User,
    ) -> Todo:
        try:
            todo = self._repository.get_by_id(todo_id, owner.id)
            if not todo:
                raise TodoNotFoundError()
            return todo

        except SQLAlchemyError as e:
            raise TodoServiceError() from e

    def get_all_for_owner(
        self,
        owner: User,
    ) -> list[Todo]:
        try:
            return self._repository.get_all_for_owner(owner.id)

        except SQLAlchemyError as e:
            raise TodoServiceError() from e

    def get_all(
        self,
    ) -> list[Todo]:
        try:
            return self._repository.get_all()

        except SQLAlchemyError as e:
            raise TodoServiceError() from e

    def create(
        self,
        todo_data: TodoRequest,
        owner: User,
    ) -> Todo:
        try:
            new_todo = self._repository.create(
                todo_data.model_dump(),
                owner.id,
            )
            self._session.commit()
            return new_todo

        except IntegrityError as e:
            self._session.rollback()
            raise TodoAlreadyExistsError() from e

        except SQLAlchemyError as e:
            self._session.rollback()
            raise TodoServiceError() from e

    def update(
        self,
        todo_data: TodoRequest,
        todo_id: int,
        owner: User,
    ) -> Todo:
        try:
            updated_todo = self._repository.update(
                todo_data.model_dump(
                    exclude_unset=True,
                    exclude_none=True,
                ),
                todo_id,
                owner.id,
            )
            if not updated_todo:
                raise TodoNotFoundError()
            self._session.commit()
            return updated_todo

        except SQLAlchemyError as e:
            self._session.rollback()
            raise TodoServiceError() from e

    def delete_for_owner(
        self,
        todo_id: int,
        owner: User,
    ) -> bool:
        try:
            success = self._repository.delete_for_owner(
                todo_id,
                owner.id,
            )
            if not success:
                raise TodoNotFoundError()
            self._session.commit()
            return True

        except SQLAlchemyError as e:
            self._session.rollback()
            raise TodoServiceError() from e

    def delete(
        self,
        todo_id: int,
    ) -> bool:
        try:
            success = self._repository.delete(todo_id)
            if not success:
                raise TodoNotFoundError()
            self._session.commit()
            return True

        except SQLAlchemyError as e:
            self._session.rollback()
            raise TodoServiceError() from e
