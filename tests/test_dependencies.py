import pytest

from app.api.dependencies import get_current_user
from app.core.security.token_manager import create_access_token
from app.exceptions.security_exceptions import HTTPValidationException


async def test_get_current_user(test_user, user_service):
    payload = {
        "sub": test_user.username,
        "id": test_user.id,
        "role": test_user.role,
    }
    token = create_access_token(data=payload)
    current_user = await get_current_user(token, user_service)

    assert current_user == test_user


async def test_get_current_user_missing_payload(user_service):
    payload = {}
    token = create_access_token(data=payload)
    with pytest.raises(HTTPValidationException) as exception_info:
        await get_current_user(token, user_service)

    assert exception_info.value.status_code == 401
    assert "Validation error" in exception_info.value.detail


async def test_get_current_user_not_found(user_service):
    payload = {
        "sub": "ghostuser",
        "id": 999,
        "role": "user",
    }
    token = create_access_token(data=payload)
    with pytest.raises(HTTPValidationException) as exception_info:
        await get_current_user(token, user_service)

    assert exception_info.value.status_code == 401
