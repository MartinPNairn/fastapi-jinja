from app.crud import get_entry
from app.models import User
from app.schemas import UserResponse
from tests.conftest import client
from app.core.security import verify_password_hash


def test_create_user(client, db):
    test_client = client()
    new_user = {
        'email': 'john@gmail.com',
        'username': 'john123',
        'first_name': 'John',
        'last_name': 'Salchijohn',
        'phone_number': 11234566,
        'role': 'user',
        'password': '12345678'
    }
    response = test_client.post("/users/create", json=new_user)
    assert response.status_code == 201
    user = get_entry(User, db, User.username == new_user["username"])
    assert user is not None


def test_get_user(client, test_user):
    test_client = client(test_user)
    response = test_client.get("/users/get-user")
    assert response.status_code == 200
    for attr, value in UserResponse.model_validate(test_user).model_dump(mode="json").items():
        assert response.json()[attr] == value


def test_update_password(client, test_user, db):
    test_client = client(test_user)
    request_data = {
        "old_password": "juan123",
        "new_password": "juan321",
    }
    response = test_client.put("/users/update-password", json=request_data)
    assert response.status_code == 204
    db.refresh(test_user)
    assert verify_password_hash(request_data["new_password"], test_user.hashed_password)


def test_update_password_invalid_current_password(client, test_user):
    test_client = client(test_user)
    request_data = {
        "old_password": "wrong_password",
        "new_password": "juan321",
    }
    response = test_client.put("/users/update-password", json=request_data)
    assert response.status_code == 401
    assert response.json() == {'detail': 'Wrong current password'}


def test_update_phone(client, test_user, db):
    test_client = client(test_user)
    request_data = {
        "phone_number": "1122334456",
    }
    response = test_client.put("/users/update-phone", json=request_data)
    assert response.status_code == 204
