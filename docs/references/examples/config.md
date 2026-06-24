# Reference: Config Layer

## src/config/settings.py

```python
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    PROTOCOL: str = "postgresql+asyncpg"
    HOST: str = "localhost"
    PORT: int = 5432
    USER: str = "postgres"
    PASSWORD: SecretStr = SecretStr("postgres")
    NAME: str = "service"

    model_config = SettingsConfigDict(env_prefix="DB_")

    @property
    def URL(self) -> SecretStr:  # noqa: N802
        return SecretStr(
            f"{self.PROTOCOL}://{self.USER}:{self.PASSWORD.get_secret_value()}"
            f"@{self.HOST}:{self.PORT}/{self.NAME}"
        )


class AppSettings(BaseSettings):
    ADDRESS: str = "127.0.0.1"
    PORT: int = 8080

    model_config = SettingsConfigDict(env_prefix="APP_")


class Settings(BaseSettings):
    DATABASE: DatabaseSettings = DatabaseSettings()
    APP: AppSettings = AppSettings()


settings = Settings()
```

## src/config/constants.py

```python
import pathlib

from pydantic_settings import BaseSettings, SettingsConfigDict


class DirSettings(BaseSettings):
    ROOT: pathlib.Path = pathlib.Path(__file__).resolve().parent.parent.parent
    SRC: pathlib.Path = ROOT / "src"

    model_config = SettingsConfigDict(env_prefix="DIR_")


class Constants(BaseSettings):
    DIRS: DirSettings = DirSettings()


constants = Constants()
```

## Notes

- Каждый settings-класс имеет свой `env_prefix`.
- `DatabaseSettings.PROTOCOL` обязателен, чтобы тесты/локальные окружения могли переопределять
  драйвер через `DB_PROTOCOL` без переписывания `URL`.
- `settings` — для runtime-конфигурации (DB, URLs, credentials, ports).
- `constants` — для путей к файлам, директориям, сертификатам.
- Секреты оборачивать в `SecretStr`, не передавать как `str`.
- Конфиг тестируется интеграционными тестами, отдельные unit-тесты не нужны.
