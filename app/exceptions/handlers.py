from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.exceptions.base import ServiceError
from app.exceptions.user_exceptions import InvalidCredentialsError, UserNotFoundError
from app.exceptions.todo_exceptions import TodoNotFoundError, TodoAlreadyExistsError



async def handle_service_error(request: Request, exception: ServiceError):
    return JSONResponse(
        status_code=500,
        content={"detail": "Database error."}
    )


async def handle_invalid_credentials_error(request: Request, exception: InvalidCredentialsError):
    return JSONResponse(
        status_code=401,
        content={"detail": "Invalid credentials."}
    )


async def handle_user_not_found_error(request: Request, exception: UserNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": "User not found."}
    )


async def handle_todo_not_found_error(request: Request, exception: TodoNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": "Todo not found."}
    )


async def handle_todo_already_exists_error(request: Request, exception: TodoAlreadyExistsError):
    return JSONResponse(
        status_code=409,
        content={"detail": "Error while creating new To-Do."}
    )


def register_exception_handlers(app: FastAPI) -> None:
    handlers = {
        InvalidCredentialsError: handle_invalid_credentials_error,
        ServiceError: handle_service_error,
        UserNotFoundError: handle_user_not_found_error,
        TodoNotFoundError: handle_todo_not_found_error,
        TodoAlreadyExistsError: handle_todo_already_exists_error,
    }
    for exc_class, handler in handlers.items():
        app.add_exception_handler(exc_class, handler)
