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
    StaleUserError,
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

    def authenticate(
        self,
        form_data: LoginCredentials,
    ) -> User:
        user = self.get_by_username(username=form_data.username)
        if not self._hasher.verify_hash(form_data.password, user.hashed_password):
            raise InvalidCredentialsError()
        return user

    def get_by_username(
        self,
        username: str,
    ) -> User:
        return self._get_user(username=username)

    def get_by_id(
        self,
        user_id: int,
    ) -> User:
        return self._get_user(id=user_id)

    def _get_user(
        self,
        **condition,
    ) -> User:
        try:
            user = self._repository.get_by_conditions(**condition)
            if user is None:
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

    def register(
        self,
        user_data: UserCreateRequest,
    ) -> User:
        try:
            data = user_data.model_dump(exclude={"password"})
            hashed_pass = self._hasher.generate_hash(user_data.password)
            data.update(hashed_password=hashed_pass.hashed_password)
            new_user = self._repository.create(data)
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
        if not self._hasher.verify_hash(pass_data.old_password, user.hashed_password):
            raise InvalidCredentialsError()
        new_hash = self._hasher.generate_hash(pass_data.new_password)
        self._update(user, {"hashed_password": new_hash.hashed_password})

    def change_phone(
        self,
        user: User,
        phone_data: ChangePhoneRequest,
    ) -> None:
        self._update(user, {"phone_number": phone_data.phone_number})

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
                raise StaleUserError()
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
