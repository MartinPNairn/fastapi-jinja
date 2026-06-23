from typing import Literal
from app.models.user import User
from app.services.auth_protocols import AuthServiceProtocol
from app.services.user_protocols import UserReadServiceProtocol
from app.core.security.security_protocols import TokenServiceProtocol


class AuthService(AuthServiceProtocol):
    def __init__(
        self,
        token_service: TokenServiceProtocol,
        user_service: UserReadServiceProtocol,
    ) -> None:
        self.token_service = token_service
        self.user_service = user_service

    def issue_access_token(
        self,
        user: User,
    ) -> str:
        data = {"sub": user.username, "id": user.id, "role": user.role}
        return self.token_service.create_access_token(data)

    def issue_refresh_token(
        self,
        user: User,
    ) -> str:
        data = {"sub": user.username}
        return self.token_service.create_refresh_token(data)

    def get_user_from_token(
        self,
        token: str,
        token_type: Literal["access", "refresh"],
    ) -> User:
        username = self.token_service.verify_token(token, token_type)
        return self.user_service.get_by_username(username)
