from typing import Annotated

from fastapi import APIRouter, status, HTTPException, Path

from app.api.dependencies import (
    TodoAdminServiceDep,
    UserAdminServiceDep,
    CurrentUserAdminDep,
)
from app.schemas import UserResponse, TodoResponse
from app.exceptions.todo_exceptions import TodoNotFoundError, TodoServiceError


router = APIRouter()


@router.get("/users", status_code=status.HTTP_200_OK)
async def get_all_users(
    user: CurrentUserAdminDep,
    user_service: UserAdminServiceDep,
) -> list[UserResponse]:
    return user_service.get_all()  # pyright: ignore[reportReturnType]


@router.get("/todos", status_code=status.HTTP_200_OK)
async def get_all_todos(
    user: CurrentUserAdminDep,
    todo_service: TodoAdminServiceDep,
) -> list[TodoResponse]:
    try:
        return todo_service.get_all()  # pyright: ignore[reportReturnType]

    except TodoServiceError as e:
        raise HTTPException(
            status_code=500,
            detail="Database error",
        ) from e


@router.delete("/todos/delete/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: CurrentUserAdminDep,
    todo_service: TodoAdminServiceDep,
    todo_id: Annotated[int, Path(gt=0)],
) -> None:
    try:
        todo_service.delete(todo_id)

    except TodoNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail="Todo not found.",
        ) from e

    except TodoServiceError as e:
        raise HTTPException(
            status_code=500,
            detail="Database error",
        ) from e
