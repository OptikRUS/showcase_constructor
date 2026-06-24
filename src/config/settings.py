from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    SECRET_KEY: SecretStr = SecretStr("secret_key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24

    model_config = SettingsConfigDict(env_prefix="AUTH_")


class Settings(BaseSettings):
    AUTH: AuthSettings = Field(default_factory=AuthSettings)


settings = Settings()
