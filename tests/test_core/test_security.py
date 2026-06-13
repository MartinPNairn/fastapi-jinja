import jwt

from app.core.security.password_hasher import authenticate_user
from app.core.security.token_manager import create_access_token

from app.core.config import get_settings


settings = get_settings()


def test_authenticate_user(test_user, session):
    password = "juan123"
    authenticated_user = authenticate_user(test_user.username, password, session)
    assert authenticated_user is not False
    assert authenticated_user.username == test_user.username

    authenticated_user = authenticate_user("aWrongUser", password, session)
    assert authenticated_user is False

    authenticated_user = authenticate_user(test_user.username, "aWrongPassword", session)
    assert authenticated_user is False


def test_create_access_token(test_user):
    data = {"sub": test_user.username, "id": test_user.id, "role": test_user.role}
    expiration_time = 15
    token = create_access_token(data=data, expiration_time_minutes=expiration_time)
    assert token is not None
    assert isinstance(token, str)

    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.HASHING_ALGORITHM])
    assert payload["id"] == test_user.id
    assert payload["sub"] == test_user.username
    assert payload["role"] == test_user.role
