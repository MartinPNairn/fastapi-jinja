from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    email: str
    username: str
    first_name: str | None = None
    last_name: str | None = None
    phone_number: int
    role: str

    model_config = ConfigDict(from_attributes=True)


class UserCreateRequest(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool


class Token(BaseModel):
    access_token: str
    token_type: str
