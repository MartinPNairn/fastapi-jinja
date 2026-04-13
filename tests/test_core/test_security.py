from datetime import timedelta
import jwt

from app.core.security import authenticate_user, create_access_token
from tests.conftest import SECRET_KEY, HASHING_ALGORITHM


def test_authenticate_user(test_user, db):
    password = "juan123"
    authenticated_user = authenticate_user(test_user.username, password, db)
    assert authenticated_user is not False
    assert authenticated_user.username == test_user.username

    authenticated_user = authenticate_user("aWrongUser", password, db)
    assert authenticated_user is False

    authenticated_user = authenticate_user(test_user.username, "aWrongPassword", db)
    assert authenticated_user is False


def test_create_access_token(test_user):
    data = {"sub": test_user.username, "id": test_user.id, "role": test_user.role}
    expiration_time = timedelta(minutes=15)
    token = create_access_token(data=data, expires_delta=expiration_time)
    assert token is not None
    assert isinstance(token, str)

    payload = jwt.decode(token, SECRET_KEY, algorithms=[HASHING_ALGORITHM])
    assert payload["id"] == test_user.id
    assert payload["sub"] == test_user.username
    assert payload["role"] == test_user.role
