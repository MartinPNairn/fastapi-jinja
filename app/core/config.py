from functools import lru_cache
from typing import Annotated
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from fastapi import Depends


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    ACCESS_TOKEN_EXPIRE_MINUTES: float = 15.0
    REFRESH_TOKEN_EXPIRE_DAYS: float = 7.0
    SECRET_KEY: str = Field(default="", min_length=1)
    HASHING_ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=".env",
    )


@lru_cache
def get_settings():
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]
