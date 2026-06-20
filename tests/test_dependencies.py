import pytest

from app.api.dependencies import get_current_user
from app.exceptions.http_exceptions import HTTPValidationException


async def test_get_current_user(test_user, token_service, user_service):
    payload = {
        "sub": test_user.username,
        "id": test_user.id,
        "role": test_user.role,
    }
    token = token_service.create_access_token(data=payload)
    current_user = await get_current_user(token, token_service, user_service)

    assert current_user == test_user


async def test_get_current_user_missing_payload(token_service, user_service):
    payload = {}
    token = token_service.create_access_token(data=payload)
    with pytest.raises(HTTPValidationException) as exception_info:
        await get_current_user(token, token_service, user_service)

    assert exception_info.value.status_code == 401
    assert "Invalid" in exception_info.value.detail


async def test_get_current_user_not_found(user_service, token_service):
    payload = {
        "sub": "ghostuser",
        "id": 999,
        "role": "user",
    }
    token = token_service.create_access_token(data=payload)
    with pytest.raises(HTTPValidationException) as exception_info:
        await get_current_user(token, token_service, user_service)

    assert exception_info.value.status_code == 401
