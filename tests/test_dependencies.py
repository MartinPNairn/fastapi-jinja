from typing import cast

import pytest
from fastapi import HTTPException

from app.services.auth_protocols import AuthServiceProtocol
from app.api.dependencies import get_current_user
from app.exceptions.http_exceptions import HTTPValidationException
from app.exceptions.user_exceptions import UserNotFoundError, UserServiceError
from app.exceptions.auth_exceptions import (
    TokenSubjectMissingError,
    WrongTokenTypeError,
    ExpiredTokenError,
    InvalidTokenError,
)


async def test_get_current_user(test_user, auth_service):
    token = auth_service.issue_access_token(test_user)
    current_user = await get_current_user(token, auth_service)
    assert current_user == test_user


@pytest.mark.parametrize(
    "raised_exception, expected_exception, expected_status",
    [
        (TokenSubjectMissingError, HTTPValidationException, 401),
        (WrongTokenTypeError, HTTPValidationException, 401),
        (ExpiredTokenError, HTTPValidationException, 401),
        (InvalidTokenError, HTTPValidationException, 401),
        (UserNotFoundError, HTTPValidationException, 401),
        (UserServiceError, HTTPException, 500),
    ],
    ids=[
        "subject_missing_401",
        "wrong_token_type_401",
        "expired_token_401",
        "invalid_token_401",
        "user_not_found_401",
        "user_service_error_500",
    ],
)
async def test_get_current_user_maps_domain_errors_to_401(
    raised_exception,
    expected_exception,
    expected_status,
):
    class RaiserAuthService:
        def get_user_from_token(self, token, token_type):
            raise raised_exception()

    with pytest.raises(expected_exception) as exception_info:
        await get_current_user(
            "some-long-token",
            cast(AuthServiceProtocol, RaiserAuthService()),
        )
    assert exception_info.value.status_code == expected_status
