from app.exceptions.base import ServiceError


class UserError(Exception):
    pass


class UserNotFoundError(UserError):
    pass


class UserAlreadyExistsError(UserError):
    pass


class StaleUserError(UserError):
    pass


class InvalidCredentialsError(UserError):
    pass


class UserServiceError(UserError, ServiceError):
    pass
