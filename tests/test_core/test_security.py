import jwt
import pytest

from app.core.security.token_service import create_access_token
from app.exceptions.user_exceptions import InvalidCredentialsError, UserNotFoundError
from app.schemas.auth import LoginCredentials
from app.core.config import get_settings


settings = get_settings() # TODO: REPLACE TOKEN FUNCTIONS WITH NEW SERVICES


def test_authenticate_user(test_user, user_service):
    login_credentials = LoginCredentials(
        username=test_user.username,
        password="juan123",
    )
    authenticated_user = user_service.authenticate(login_credentials)
    assert authenticated_user.username == test_user.username


def test_authenticate_user_wrong_user(user_service):
    login_credentials = LoginCredentials(
        username="aWrongUser",
        password="juan123",
    )
    with pytest.raises(UserNotFoundError):
        user_service.authenticate(login_credentials)


def test_authenticate_user_wrong_password(test_user, user_service):
    login_credentials = LoginCredentials(
        username=test_user.username,
        password="aWrongPassword",
    )
    with pytest.raises(InvalidCredentialsError):
        user_service.authenticate(login_credentials)


def test_create_access_token(test_user):
    data = {"sub": test_user.username, "id": test_user.id, "role": test_user.role}
    expiration_time = 15
    token = create_access_token(data=data, expiration_time_minutes=expiration_time)
    assert token is not None
    assert isinstance(token, str)

    payload = jwt.decode(
        token, settings.SECRET_KEY, algorithms=[settings.HASHING_ALGORITHM]
    )
    assert payload["id"] == test_user.id
    assert payload["sub"] == test_user.username
    assert payload["role"] == test_user.role
