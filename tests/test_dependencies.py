import pytest

from app.api.dependencies import get_current_user
from app.exceptions.http_exceptions import HTTPValidationException


async def test_get_current_user(test_user, auth_service):
    token = auth_service.issue_access_token(test_user)
    current_user = await get_current_user(token, auth_service)
    assert current_user == test_user

 # TODO: ADD TOKEN VERIFICATION TESTS TO SECURITY TESTS
# async def test_get_current_user_missing_payload(token_service, auth_service):
#     payload = {}
#     token = token_service.create_access_token(data=payload)
#     with pytest.raises(HTTPValidationException) as exception_info:
#         await get_current_user(token, token_service, user_service)

#     assert exception_info.value.status_code == 401
#     assert "Invalid" in exception_info.value.detail


async def test_get_current_user_not_found(test_ghost_user, auth_service):
    token = auth_service.issue_access_token(test_ghost_user)
    with pytest.raises(HTTPValidationException) as exception_info:
        await get_current_user(token, auth_service)

    assert exception_info.value.status_code == 401
