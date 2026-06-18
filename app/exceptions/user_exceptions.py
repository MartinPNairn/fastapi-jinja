class UserError(Exception):
    pass


class UserNotFoundError(UserError):
    pass


class UserAlreadyExistsError(UserError):
    pass


class UserServiceError(UserError):
    pass


class StaleUserError(UserError):
    pass


class InvalidCredentialsError(UserError):
    pass
