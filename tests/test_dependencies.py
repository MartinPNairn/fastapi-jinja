import pytest
from fastapi import HTTPException

from app.api.dependencies import get_current_user
from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_get_current_user(test_user, db):
    payload = {"sub": test_user.username, "id": test_user.id, "role": test_user.role}
    token = create_access_token(data=payload)

    current_user = await get_current_user(token, db)
    assert current_user == test_user


@pytest.mark.asyncio
async def test_get_current_user_missing_payload(test_user, db):
    payload = {}
    token = create_access_token(data=payload)

    with pytest.raises(HTTPException) as exception_info:
        await get_current_user(token, db)

    assert exception_info.value.status_code == 401
    assert exception_info.value.detail == "Could not validate credentials!"
