from fastapi import HTTPException


class InvalidCredentialsException(HTTPException):
    def __init__(self, detail: str = "Could not validate credentials!") -> None:
        super().__init__(
            status_code=401,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )
