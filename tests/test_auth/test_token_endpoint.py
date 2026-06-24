def test_login_for_access_token_success(client, test_user):
    response = client().post(
        "/auth/login",
        data={"username": "juanperez", "password": "juan123"},
    )
    assert response.status_code == 200
    assert isinstance(response.json()["access_token"], str)


def test_login_for_access_token_invalid_password(client, test_user):
    response = client().post(
        "/auth/login",
        data={"username": "juanperez", "password": "a-wrong-password-mate"},
    )
    assert response.status_code == 401
    assert "Invalid" in response.json()["detail"]


def test_login_for_access_token_wrong_data_type(client, test_user):
    response = client().post(
        "/auth/login",
        json={"username": "juanperez", "password": "secret"},
    )
    assert response.status_code == 422


def test_login_for_access_token_wrong_or_no_data(client, test_user):
    response = client().post(
        "/auth/login",
        data={"asdsd": "alksdjals"},
    )
    fields = [error["loc"][-1] for error in response.json()["detail"]]
    assert response.status_code == 422
    assert "username" in fields
    assert "password" in fields
