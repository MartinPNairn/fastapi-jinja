from typing import Annotated

from fastapi import APIRouter, Path, HTTPException, status

from app.api.dependencies import CurrentUserDep
from app.schemas import TodoResponse, TodoRequest
from app.repositories.todo_repository import (
    TodoReaderRepoDep,
    TodoWriterRepoDep,
    DatabaseError,
)


router = APIRouter()


@router.get("/all", status_code=status.HTTP_200_OK)
async def read_all(
    user: CurrentUserDep,
    todo_reader_repo: TodoReaderRepoDep,
) -> list[TodoResponse]:
    all_todos = todo_reader_repo.get_all_todos(user.id)
    return [TodoResponse.model_validate(todo) for todo in all_todos]


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_todo(
    user: CurrentUserDep,
    todo_data: TodoRequest,
    todo_writer_repo: TodoWriterRepoDep,
) -> TodoResponse:
    try:
        new_todo = todo_writer_repo.create_todo(todo_data.model_dump(), user.id)
        return TodoResponse.model_validate(new_todo)
    except DatabaseError:
        raise HTTPException(
            status_code=500,
            detail="Error while creating new To-Do.",
        )


@router.put("/update/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    todo_id: Annotated[int, Path(title="To-do's ID.", gt=-1)],
    new_todo_data: TodoRequest,
    user: CurrentUserDep,
    todo_writer_repo: TodoWriterRepoDep,
):
    updated = todo_writer_repo.update_todo(
        new_todo_data.model_dump(exclude_unset=True, exclude_none=True),
        todo_id,
        user.id,
    )
    if not updated:
        raise HTTPException(
            status_code=404, 
            detail="To-Do to update not found",
        )


@router.delete("/delete/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: Annotated[int, Path(title="To-do's ID.", gt=-1)],
    todo_writer_repo: TodoWriterRepoDep,
    user: CurrentUserDep,
):  
    deleted = todo_writer_repo.delete_todo(
        todo_id, 
        user.id,
    )
    if not deleted:
        raise HTTPException(
            status_code=404, 
            detail="To-Do to delete not found.",
        )


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo(
    todo_id: Annotated[int, Path(title="Todo's ID.", gt=-1)],
    todo_reader_repo: TodoReaderRepoDep,
    user: CurrentUserDep,
) -> TodoResponse:
    todo = todo_reader_repo.get_todo_by_id(todo_id, user.id)
    if not todo:
        raise HTTPException(
            status_code=404, 
            detail="To-Do not found.",
        )
    return TodoResponse.model_validate(todo)
