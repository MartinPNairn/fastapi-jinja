from fastapi import HTTPException


class HTTPValidationException(HTTPException):
    def __init__(self, status_code: int = 400, detail: str = "Validation error.") -> None:
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )
