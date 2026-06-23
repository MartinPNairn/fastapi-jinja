from typing import Protocol, Literal
from app.models.user import User


class AuthServiceProtocol(Protocol):
    def issue_access_token(self, user: User) -> str: ...

    def issue_refresh_token(self, user: User) -> str: ...

    def get_user_from_token(self, token: str, token_type: Literal["access", "refresh"]) -> User: ...
