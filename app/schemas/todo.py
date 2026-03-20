from pydantic import BaseModel, Field, ConfigDict


class TodoRequest(BaseModel):
    title: str | None = Field(min_length=3, max_length=60)
    description: str | None = Field(max_length=100)
    priority: int | None = Field(gt=0, lt=6)
    complete: bool | None = Field(default=False)

    model_config = ConfigDict(from_attributes=True)


class TodoResponse(TodoRequest):
    id: int
    owner_id: int
