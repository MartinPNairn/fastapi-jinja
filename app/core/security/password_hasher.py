from app.schemas import HashedPassword
from app.core.security.


class PasswordHasher:
    def __init__(self, hasher: object) -> None:
        self._hasher = hasher

    def hash(self, raw_password: str) -> HashedPassword: 
        ...

    def verify(self, raw_password: str, hashed_password: HashedPassword) -> bool: 
        ...
    