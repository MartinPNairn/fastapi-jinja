from typing import Annotated

from fastapi import APIRouter, status, HTTPException, Path

from app.api.dependencies import CurrentUserDep, SessionDep
from app.schemas import UserResponse, TodoResponse
from app.crud import get_all_entries, delete_entry
from app.models import Todo, User


router = APIRouter()


# Get all users
@router.get("/users", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
async def get_all_users(user: CurrentUserDep, db: SessionDep) -> list[UserResponse]:
    if not user or user.role.casefold() != "admin":
        raise HTTPException(status_code=401, detail="Authentication failed.")
    all_users = get_all_entries(User, db)
    if not all_users:
        raise HTTPException(status_code=404, detail="No users found in database.")
    return all_users


# Get all To-Dos
@router.get("/todos", status_code=status.HTTP_200_OK, response_model=list[TodoResponse])
async def get_all_todos(user: CurrentUserDep, db: SessionDep) -> list[TodoResponse]:
    if not user or user.role.casefold() != "admin":
        raise HTTPException(status_code=401, detail="Authentication failed.")
    all_todos = get_all_entries(Todo, db)
    if not all_todos:
        raise HTTPException(status_code=404, detail="No To-Dos found in database.")
    return all_todos


@router.delete("/todos/delete/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: CurrentUserDep, db: SessionDep, todo_id: Annotated[int, Path(gt=0)]):
    if not user or user.role.casefold() != "admin":
        raise HTTPException(status_code=401, detail="Authentication failed.")
    entry_deleted = delete_entry(todo_id, Todo, db)
    if not entry_deleted:
        raise HTTPException(status_code=404, detail="Todo not found.")
