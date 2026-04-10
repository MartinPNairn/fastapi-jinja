import jwt
import pytest
from fastapi import HTTPException

from tests.conftest import SECRET_KEY, HASHING_ALGORITHM
from app.api.dependencies import get_current_user


@pytest.mark.asyncio
async def test_get_current_user(test_user, db):
    payload = {"sub": test_user.username, "id": test_user.id, "role": test_user.role}
    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=HASHING_ALGORITHM)

    current_user = await get_current_user(token, db)
    assert current_user == test_user


@pytest.mark.asyncio
async def test_get_current_user_missing_payload(test_user, db):
    payload = {}
    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=HASHING_ALGORITHM)

    with pytest.raises(HTTPException) as exception_info:
        await get_current_user(token, db)

    assert exception_info.value.status_code == 401
    assert exception_info.value.detail == "Could not validate credentials!"
