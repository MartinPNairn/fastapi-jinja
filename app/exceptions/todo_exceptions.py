from app.exceptions.base import ServiceError


class TodoError(Exception):
    pass


class TodoNotFoundError(TodoError):
    pass


class TodoAlreadyExistsError(TodoError):
    pass


class TodoServiceError(TodoError, ServiceError):
    pass
