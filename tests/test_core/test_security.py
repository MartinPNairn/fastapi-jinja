import pytest

from app.exceptions.user_exceptions import InvalidCredentialsError, UserNotFoundError
from app.exceptions.auth_exceptions import InvalidTokenError
from app.schemas.auth import LoginCredentials


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


def test_issue_access_token(test_user, auth_service, token_service):
    token = auth_service.issue_access_token(test_user)
    assert token is not None
    username = token_service.verify_token(token, "access")
    assert username == test_user.username


def test_issue_refresh_token(test_user, auth_service, token_service):
    token = auth_service.issue_refresh_token(test_user)
    assert token is not None
    username = token_service.verify_token(token, "refresh")
    assert username == test_user.username


def test_get_user_from_access_token(test_user, auth_service):
    token = auth_service.issue_access_token(test_user)
    assert token is not None
    user = auth_service.get_user_from_token(token, "access")
    assert user == test_user


def test_get_user_from_access_token_ghost_user(test_ghost_user, auth_service):
    token = auth_service.issue_access_token(test_ghost_user)
    assert token is not None
    with pytest.raises(UserNotFoundError):
        auth_service.get_user_from_token(token, "access")


def test_get_user_from_access_token_no_token(auth_service):
    token = None
    with pytest.raises(InvalidTokenError):
        auth_service.get_user_from_token(token, "access")
