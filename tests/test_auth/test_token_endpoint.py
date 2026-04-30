

def test_login_for_access_token_success(client, mock_security):
    response = client().post(
        "/auth/login", 
        data={"username": "john", "password": "secret"},
    )
    response_data = response.json()

    assert response.status_code == 200
    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"
    assert isinstance(response_data["access_token"], str)


def test_login_for_access_token_invalid_password(client, mock_security):
    response = client().post(
        "/auth/login", 
        data={"username": "john", "password": "a-wrong-password-mate"},
    )
    response_data = response.json()

    assert response.status_code == 401
    assert "Could not" in response_data["detail"]


def test_login_for_access_token_wrong_data_type(client, mock_security):
    response = client().post(
        "/auth/login", 
        json={"username": "john", "password": "secret"},
    )

    assert response.status_code == 422


def test_login_for_access_token_wrong_or_no_data(client, mock_security):
    response = client().post(
        "/auth/login", 
        data={"asdsd": "alksdjals"},
    )
    response_data = response.json()

    fields = [error["loc"][-1] for error in response_data["detail"]]
    assert response.status_code == 422
    assert "username" in fields
    assert "password" in fields