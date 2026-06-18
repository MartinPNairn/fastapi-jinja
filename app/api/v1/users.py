from fastapi import APIRouter, status, HTTPException
from app.api.dependencies import CurrentUserDep, UserWriteServiceDep
from app.exceptions.user_exceptions import (
    UserServiceError,
    UserAlreadyExistsError,
    InvalidCredentialsError,
)
from app.exceptions.security_exceptions import HTTPValidationException
from app.schemas import (
    ChangePasswordRequest,
    ChangePhoneRequest,
    UserCreateRequest,
    UserResponse,
)

router = APIRouter()


# Create a new user
@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_service: UserWriteServiceDep,
    user_create_request: UserCreateRequest,
) -> UserResponse:
    try:
        new_user = user_service.register(user_create_request)
        return new_user  # pyright: ignore[reportReturnType]

    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=409,
        ) from e

    except UserServiceError as e:
        raise HTTPException(
            status_code=500,
        ) from e


@router.get("/get-user", status_code=status.HTTP_200_OK)
async def get_user(
    user: CurrentUserDep,
) -> UserResponse:
    return user  # pyright: ignore[reportReturnType]


@router.put("/update-password", status_code=status.HTTP_204_NO_CONTENT)
async def update_password(
    user: CurrentUserDep,
    user_service: UserWriteServiceDep,
    new_data: ChangePasswordRequest,
) -> None:
    try:
        user_service.change_password(user, new_data)

    except InvalidCredentialsError as e:
        raise HTTPValidationException(
            status_code=401, detail="Wrong current password."
        ) from e

    except UserServiceError as e:
        raise HTTPException(
            status_code=500,
        ) from e


@router.put("/update-phone", status_code=status.HTTP_204_NO_CONTENT)
async def update_phone(
    user: CurrentUserDep,
    user_service: UserWriteServiceDep,
    new_data: ChangePhoneRequest,
) -> None:
    try:
        user_service.change_phone(user, new_data)

    except UserServiceError as e:
        raise HTTPException(
            status_code=500,
        ) from e
