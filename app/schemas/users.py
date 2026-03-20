from pydantic import BaseModel


class UpdatePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class HashedPassword(BaseModel):
    hashed_password: str


class UpdatePhoneRequest(BaseModel):
    phone_number: int
