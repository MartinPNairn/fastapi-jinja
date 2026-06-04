class TodoError(Exception):
    pass


class TodoNotFoundError(TodoError):
    pass


class TodoAlreadyExistsError(TodoError):
    pass


class TodoServiceError(TodoError):
    pass
