class BaseTokenError(Exception):
    """Base exception for all JWT-related errors."""


class TokenSubjectMissingError(BaseTokenError):
    pass


class WrongTokenTypeError(BaseTokenError):
    pass


class ExpiredTokenError(BaseTokenError):
    pass


class InvalidTokenError(BaseTokenError):
    pass
