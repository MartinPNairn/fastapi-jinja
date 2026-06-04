from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.models.todo import Todo
from app.repositories.todo_repository import TodoRepository


class TodoError(Exception):
    pass


class TodoService:
    def __init__(self, repository: TodoRepository, session: Session) -> None:
        self._repository = repository
        self._session = session

    def get_by_id(self, todo_id: int, owner_id: int) -> Todo | None:
        return self._repository.get_by_id(todo_id, owner_id)

    def get_all_for_owner(self, owner_id: int) -> list[Todo]: 
        return self._repository.get_all_for_owner(owner_id)

    def get_all(self) -> list[Todo]: 
        return self._repository.get_all()

    def create(self, todo_data: dict, owner_id: int) -> Todo: 
        try:
            new_todo = self._repository.create(todo_data, owner_id)
            self._session.commit()
            return new_todo
        
        except IntegrityError as e:
            self._session.rollback()
            raise TodoError("Todo with the same title already exists") from e

        except SQLAlchemyError as e:
            self._session.rollback()
            raise TodoError("Failed to create todo") from e
            
    def update(self, todo_data: dict, todo_id: int, owner_id: int) -> Todo | None: 
        try:
            updated_todo = self._repository.update(todo_data, todo_id, owner_id)
            if not updated_todo:
                raise TodoError("Todo not found")
            
            self._session.commit()
            return updated_todo
        
        except SQLAlchemyError as e:
            raise TodoError("Failed to update todo") from e

    def delete_for_owner(self, todo_id: int, owner_id: int) -> bool: 
        try:
            success = self._repository.delete_for_owner(todo_id, owner_id)
            if not success:
                raise TodoError("Todo not found or not owned by user")
            
            self._session.commit()
            return True
        
        except SQLAlchemyError as e:
            self._session.rollback()
            raise TodoError("Failed to delete todo") from e

    def delete(self, todo_id: int) -> bool: 
        try:
            success = self._repository.delete(todo_id)
            if not success:
                raise TodoError("Todo not found")
            
            self._session.commit()
            return True
        
        except SQLAlchemyError as e:
            self._session.rollback()
            raise TodoError("Failed to delete todo") from e
