from app.schemas import UserResponse
from app.core.security.password_hasher import PwdlibPasswordHasher


def test_create_user(client, user_service):
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
    user = user_service.get_by_username(new_user["username"])
    assert user.email == new_user["email"]


def test_get_user(client, test_user):
    test_client = client(test_user)
    response = test_client.get("/users/get-user")
    assert response.status_code == 200
    assert response.json() == UserResponse.model_validate(test_user).model_dump(mode="json")
   

def test_update_password(client, test_user, session):
    test_client = client(test_user)
    request_data = {
        "old_password": "juan123",
        "new_password": "juan321",
    }
    response = test_client.put("/users/update-password", json=request_data)
    assert response.status_code == 204
    session.refresh(test_user)
    assert PwdlibPasswordHasher().verify_hash(request_data["new_password"], test_user.hashed_password)


def test_update_password_invalid_current_password(client, test_user):
    test_client = client(test_user)
    request_data = {
        "old_password": "wrong_password",
        "new_password": "juan321",
    }
    response = test_client.put("/users/update-password", json=request_data)
    assert response.status_code == 401
    assert response.json() == {'detail': 'Wrong current password.'}


def test_update_phone(client, test_user, session):
    test_client = client(test_user)
    request_data = {
        "phone_number": "1122334456",
    }
    response = test_client.put("/users/update-phone", json=request_data)
    assert response.status_code == 204
