from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    SECRET_KEY: SecretStr = SecretStr("secret_key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24

    model_config = SettingsConfigDict(env_prefix="AUTH_")


class DatabaseSettings(BaseSettings):
    PROTOCOL: str = "postgresql+asyncpg"
    HOST: str = "localhost"
    PORT: int = 5432
    USER: str = "postgres"
    PASSWORD: SecretStr = SecretStr("postgres")
    NAME: str = "showcase_constructor"
    URL: SecretStr = SecretStr("")

    model_config = SettingsConfigDict(env_prefix="DB_")

    def model_post_init(self, __context: object, /) -> None:
        self.URL = SecretStr(
            f"{self.PROTOCOL}://{self.USER}:{self.PASSWORD.get_secret_value()}"
            f"@{self.HOST}:{self.PORT}/{self.NAME}"
        )


class Settings(BaseSettings):
    AUTH: AuthSettings = Field(default_factory=AuthSettings)
    DATABASE: DatabaseSettings = Field(default_factory=DatabaseSettings)


settings = Settings()
