class TokenError(Exception):
    """
    Base exception for all JWT-related errors.
    """
    pass


class TokenSubjectMissingError(TokenError):
    pass


class WrongTokenTypeError(TokenError):
    pass


class ExpiredTokenError(TokenError):
    pass


class InvalidTokenError(TokenError):
    pass
