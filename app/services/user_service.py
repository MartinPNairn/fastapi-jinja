from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.models.user import User
from app.schemas.users import ChangePasswordRequest, ChangePhoneRequest
from app.schemas.auth import UserCreateRequest
from app.repositories.user_repository import UserRepository
from app.exceptions.user_exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
    UserServiceError,
)


class TodoService:
    def __init__(self, repository: UserRepository, session: Session) -> None:
        self._repository = repository
        self._session = session

    def get_by_id(
        self,
        user_id: int,
    ) -> User:
        try:
            user = self._repository.get_by_id(user_id)
            if not user:
                raise UserNotFoundError()
            return user

        except SQLAlchemyError as e:
            raise UserServiceError() from e

    def get_all(
        self,
    ) -> list[User]:
        try:
            return self._repository.get_all()

        except SQLAlchemyError as e:
            raise UserServiceError() from e

    def create(
        self,
        user_data: UserCreateRequest,
    ) -> User:
        try:
            new_user = self._repository.create(
                user_data.model_dump(),
            )
            self._session.commit()
            return new_user

        except IntegrityError as e:
            self._session.rollback()
            raise UserAlreadyExistsError() from e

        except SQLAlchemyError as e:
            self._session.rollback()
            raise UserServiceError() from e

    def change_password(
        self,
        user: User,
        pass_data: ChangePasswordRequest,
    ) -> User:
        # TODO: ADD PASSWORD VERIFICATION LOGIC
        data = pass_data.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )
        return self._update(user, data)

    def change_phone(
        self,
        user: User,
        new_data: ChangePhoneRequest,
    ) -> User:
        data = new_data.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )
        return self._update(user, data)
        
    def _update(
        self, 
        user: User, 
        new_data: dict,
    ) -> User:
        try:
            updated_user = self._repository.update(
                user.id,
                new_data,
            )
            if not updated_user:
                raise UserNotFoundError()
            self._session.commit()
            return updated_user

        except SQLAlchemyError as e:
            self._session.rollback()
            raise UserServiceError() from e

    def delete(
        self,
        user_id: int,
    ) -> bool:
        try:
            success = self._repository.delete(user_id)
            if not success:
                raise UserNotFoundError()
            self._session.commit()
            return True

        except SQLAlchemyError as e:
            self._session.rollback()
            raise UserServiceError() from e
