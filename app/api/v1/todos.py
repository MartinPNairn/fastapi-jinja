from typing import Annotated

from fastapi import APIRouter, Path, HTTPException, status

from app.api.dependencies import SessionDep, CurrentUserDep
from app.models import Todo
from app.schemas import TodoResponse, TodoRequest
from app.crud import get_entry, create_entry, update_entry, get_all_entries, delete_entry, DatabaseError

router = APIRouter()


@router.get("/all", status_code=status.HTTP_200_OK, response_model=list[TodoResponse])
async def read_all(user: CurrentUserDep, db: SessionDep):
    all_todos = get_all_entries(Todo, db, Todo.owner_id == user.id)
    if not all_todos:
        raise HTTPException(404, detail="No To-Dos found.")
    return all_todos


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=TodoResponse)
async def create_todo(user: CurrentUserDep, todo_data: TodoRequest, db: SessionDep) -> TodoResponse:
    new_todo = Todo(**todo_data.model_dump(), owner_id=user.id)
    try:
        create_entry(new_todo, db)
        return new_todo
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=f"Error while creating new To-Do. Rolling back. Error: {e}")


@router.put("/update/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
        todo_id: Annotated[int, Path(title="To-do's ID.", gt=-1)],
        todo_data: TodoRequest,
        user: CurrentUserDep,
        db: SessionDep,
):
    todo_to_update = get_entry(Todo, db, Todo.id == todo_id)
    if not todo_to_update:
        raise HTTPException(status_code=404, detail="To-Do to update not found. Rolling back.")
    if todo_to_update.owner_id != user.id:
        raise HTTPException(status_code=403, detail="To-Do to update not linked to current user.")
    if not update_entry(todo_id, Todo, todo_data, db):
        raise HTTPException(status_code=404, detail="To-Do to update not found. Rolling back.")


@router.delete("/delete/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: Annotated[int, Path(title="To-do's ID.", gt=-1)], db: SessionDep, user: CurrentUserDep):
    todo_to_delete = get_entry(Todo, db, Todo.id == todo_id)
    if not todo_to_delete:
        raise HTTPException(status_code=404, detail="To-Do to delete not found. Rolling back.")
    if todo_to_delete.owner_id != user.id:
        raise HTTPException(status_code=403, detail="To-Do to delete not linked to current user.")
    if not delete_entry(todo_id, Todo, db):
        raise HTTPException(status_code=404, detail="To-Do to delete not found. Rolling back.")


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK, response_model=TodoResponse)
async def get_todo(todo_id: Annotated[int, Path(title="Todo's ID.", gt=-1)], db: SessionDep) -> TodoResponse:
    todo = get_entry(Todo, db, Todo.id == todo_id)
    if not todo:
        raise HTTPException(404, detail="To-Do not found.")
    return todo
