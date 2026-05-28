from typing import Annotated

from fastapi import APIRouter, status, HTTPException, Path

from app.api.dependencies import CurrentUserDep, SessionDep
from app.schemas import UserResponse, TodoResponse
from app.repositories.todo_repository import TodoReaderRepoDep, TodoWriterRepoDep
from app.crud import get_all_entries
from app.models import User


router = APIRouter()


@router.get("/users", status_code=status.HTTP_200_OK)
async def get_all_users(
    user: CurrentUserDep,
    db: SessionDep,
) -> list[UserResponse]:
    if not user or user.role.casefold() != "admin":
        raise HTTPException(status_code=401, detail="Authentication failed.")
    all_users = get_all_entries(User, db)
    if not all_users:
        raise HTTPException(status_code=404, detail="No users found in database.")
    return [UserResponse.model_validate(user) for user in all_users]


@router.get("/todos", status_code=status.HTTP_200_OK)
async def get_all_todos(
    user: CurrentUserDep,
    todo_reader_repo: TodoReaderRepoDep,
) -> list[TodoResponse]:
    if not user or user.role.casefold() != "admin":
        raise HTTPException(status_code=401, detail="Authentication failed.")
    all_todos = todo_reader_repo.get_all_todos()
    if not all_todos:
        raise HTTPException(status_code=404, detail="No To-Dos found in database.")
    return [TodoResponse.model_validate(todo) for todo in all_todos]


@router.delete("/todos/delete/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: CurrentUserDep,
    todo_writer_repo: TodoWriterRepoDep,
    todo_id: Annotated[int, Path(gt=0)],
):
    if not user or user.role.casefold() != "admin":
        raise HTTPException(status_code=401, detail="Authentication failed.")
    entry_deleted = todo_writer_repo.delete_todo(todo_id)
    if not entry_deleted:
        raise HTTPException(status_code=404, detail="Todo not found.")
