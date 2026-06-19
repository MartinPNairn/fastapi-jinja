from pwdlib import PasswordHash

from app.schemas import HashedPassword


password_hasher = PasswordHash.recommended()


class PwdlibPasswordHasher:
    def __init__(self) -> None:
        self._hasher = PasswordHash.recommended()

    def generate_hash(self, raw_password: str) -> HashedPassword:
        hashed_pass = self._hasher.hash(raw_password)
        return HashedPassword(hashed_password=hashed_pass)

    def verify_hash(self, raw_password: str, hashed_password: str) -> bool:
        return self._hasher.verify(raw_password, hashed_password)
