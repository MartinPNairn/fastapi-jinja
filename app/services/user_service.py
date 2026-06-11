from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.models.user import User
from app.schemas.users import ChangePasswordRequest, ChangePhoneRequest
from app.schemas.auth import UserCreateRequest, LoginCredentials
from app.repositories.user_protocols import UserRepositoryProtocol
from app.services.user_protocols import UserServiceProtocol
from app.core.security.security_protocols import PasswordHasherProtocol
from app.exceptions.user_exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
    UserServiceError,
    InvalidCredentialsError,
)


class UserService(UserServiceProtocol):
    def __init__(
        self,
        repository: UserRepositoryProtocol,
        password_hasher: PasswordHasherProtocol,
        session: Session,
    ) -> None:
        self._repository = repository
        self._hasher = password_hasher
        self._session = session

    def get_by_id(
        self,
        user_id: int,
    ) -> User:
        try:
            user = self._repository.get_by_conditions(id=user_id)
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

    def authenticate(
        self, 
        form_data: LoginCredentials,
    ) -> User:
        try:
            user = self._repository.get_by_conditions(username=form_data.username)
            if user is None:
                raise UserNotFoundError()
            if not self._hasher.verify_hash(form_data.password, user.hashed_password):
                raise InvalidCredentialsError()
            return user
        
        except SQLAlchemyError as e:
            raise UserServiceError() from e

    def create_account(
        self,
        user_data: UserCreateRequest,
    ) -> User:
        try:
            data = user_data.model_dump(exclude={"password"})
            hashed_pass = self._hasher.generate_hash(user_data.password)
            data.update(hashed_password=hashed_pass.hashed_password)
            new_user = self._repository.create(
                data,
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
    ) -> None:
        # TODO: ADD PASSWORD VERIFICATION LOGIC

        data = pass_data.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )
        self._update(user, data)

    def change_phone(
        self,
        user: User,
        phone_data: ChangePhoneRequest,
    ) -> None:
        data = phone_data.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )
        self._update(user, data)

    def _update(
        self,
        user: User,
        new_data: dict,
    ) -> None:
        try:
            updated_user = self._repository.update(
                user.id,
                new_data,
            )
            if not updated_user:
                raise UserNotFoundError()
            self._session.commit()

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
