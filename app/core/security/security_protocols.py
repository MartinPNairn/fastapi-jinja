from typing import Protocol
from app.schemas import HashedPassword


class PasswordHasher(Protocol):
    def hash(self, raw_password: str) -> HashedPassword: ...

    def verify(self, raw_password: str, hashed_password: HashedPassword) -> bool: ...
    