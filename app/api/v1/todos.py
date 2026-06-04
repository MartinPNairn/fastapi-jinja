from typing import Annotated

from fastapi import APIRouter, Path, HTTPException, status

from app.api.dependencies import CurrentUserDep, TodoReadServiceDep, TodoWriteServiceDep
from app.schemas import TodoResponse, TodoRequest
from app.exceptions.todo_exceptions import (
    TodoServiceError,
    TodoAlreadyExistsError,
    TodoNotFoundError,
)

router = APIRouter()


@router.get("/all", status_code=status.HTTP_200_OK)
async def read_all(
    user: CurrentUserDep,
    todo_service: TodoReadServiceDep,
) -> list[TodoResponse]:
    try:
        all_todos = todo_service.get_all_for_owner(user.id)
        return [TodoResponse.model_validate(todo) for todo in all_todos]

    except TodoServiceError as e:
        raise HTTPException(
            status_code=500,
            detail="Database error.",
        ) from e


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_todo(
    user: CurrentUserDep,
    todo_data: TodoRequest,
    todo_service: TodoWriteServiceDep,
) -> TodoResponse:
    try:
        new_todo = todo_service.create(todo_data.model_dump(), user.id)
        return TodoResponse.model_validate(new_todo)

    except TodoAlreadyExistsError as e:
        raise HTTPException(
            status_code=500,
            detail="Error while creating new To-Do.",
        ) from e


@router.put("/update/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    todo_id: Annotated[int, Path(title="To-do's ID.", gt=-1)],
    new_todo_data: TodoRequest,
    user: CurrentUserDep,
    todo_service: TodoWriteServiceDep,
) -> None:
    try:
        todo_service.update(
            new_todo_data.model_dump(exclude_unset=True, exclude_none=True),
            todo_id,
            user.id,
        )

    except TodoNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail="To-Do to update not found.",
        ) from e

    except TodoServiceError as e:
        raise HTTPException(
            status_code=500,
            detail="Database error.",
        ) from e


@router.delete("/delete/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: Annotated[int, Path(title="To-do's ID.", gt=-1)],
    todo_service: TodoWriteServiceDep,
    user: CurrentUserDep,
) -> None:
    try:
        todo_service.delete_for_owner(
            todo_id,
            user.id,
        )

    except TodoNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail="To-Do to delete not found.",
        ) from e

    except TodoServiceError as e:
        raise HTTPException(
            status_code=500,
            detail="Database error.",
        ) from e


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo(
    todo_id: Annotated[int, Path(title="Todo's ID.", gt=-1)],
    todo_service: TodoReadServiceDep,
    user: CurrentUserDep,
) -> TodoResponse:
    todo = todo_service.get_by_id(todo_id, user.id)
    if not todo:
        raise HTTPException(
            status_code=404,
            detail="To-Do not found.",
        )
    return TodoResponse.model_validate(todo)
