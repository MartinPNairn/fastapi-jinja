from pydantic import BaseModel


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class HashedPassword(BaseModel):
    hashed_password: str


class ChangePhoneRequest(BaseModel):
    phone_number: int
