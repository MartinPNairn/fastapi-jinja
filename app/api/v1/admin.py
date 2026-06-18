from typing import Annotated

from fastapi import APIRouter, status, HTTPException, Path

from app.api.dependencies import CurrentUserDep, SessionDep, TodoAdminServiceDep
from app.schemas import UserResponse, TodoResponse
from app.crud import get_all_entries
from app.models import User
from app.exceptions.todo_exceptions import TodoNotFoundError, TodoServiceError


router = APIRouter()

# TODO: IMPLEMENT USER SERVICE ON THIS ENDPOINTS

@router.get("/users", status_code=status.HTTP_200_OK)
async def get_all_users(
    user: CurrentUserDep,
    session: SessionDep,
) -> list[UserResponse]:
    if not user or user.role.casefold() != "admin":
        raise HTTPException(status_code=401, detail="Authorization failed.")
    all_users = get_all_entries(User, session)
    if not all_users:
        raise HTTPException(status_code=404, detail="No users found in database.")
    return [UserResponse.model_validate(user) for user in all_users]


@router.get("/todos", status_code=status.HTTP_200_OK)
async def get_all_todos(
    user: CurrentUserDep,
    todo_service: TodoAdminServiceDep,
) -> list[TodoResponse]:
    if not user or user.role.casefold() != "admin":
        raise HTTPException(status_code=401, detail="Authorization failed.")
    all_todos = todo_service.get_all()
    if not all_todos:
        raise HTTPException(status_code=404, detail="No To-Dos found in database.")
    return [TodoResponse.model_validate(todo) for todo in all_todos]


@router.delete("/todos/delete/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: CurrentUserDep,
    todo_service: TodoAdminServiceDep,
    todo_id: Annotated[int, Path(gt=0)],
):
    try:
        if not user or user.role.casefold() != "admin":
            raise HTTPException(
                status_code=401,
                detail="Authorization failed.",
            )
        todo_service.delete(todo_id)

    except TodoNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail="Todo not found.",
        ) from e
