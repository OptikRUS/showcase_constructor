from pathlib import Path

from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from src.config import settings as settings_module
from src.config.constants import constants
from src.storages import database as database_module


class TestDatabaseSettings:
    def test_url_uses_db_components(self) -> None:
        assert hasattr(settings_module, "DatabaseSettings")
        database_settings_type = settings_module.DatabaseSettings
        database = database_settings_type(
            PROTOCOL="postgresql+asyncpg",
            HOST="db.test",
            PORT=5433,
            USER="user",
            PASSWORD=SecretStr("pass"),
            NAME="showcase_test",
        )

        assert database.URL.get_secret_value() == (
            "postgresql+asyncpg://user:pass@db.test:5433/showcase_test"
        )

    def test_settings_exposes_database_settings(self) -> None:
        assert hasattr(settings_module.settings, "DATABASE")

        assert isinstance(settings_module.settings.DATABASE, settings_module.DatabaseSettings)


class TestConstants:
    def test_constants_expose_project_directories(self) -> None:
        expected_root = Path(__file__).resolve().parents[3]

        assert expected_root == constants.DIRS.ROOT
        assert constants.DIRS.SRC == constants.DIRS.ROOT / "src"


class TestDatabaseSessionFactory:
    def test_database_module_exposes_async_engine_and_session_factory(self) -> None:
        assert isinstance(database_module.async_engine, AsyncEngine)
        assert isinstance(database_module.async_session, async_sessionmaker)
        assert database_module.async_session.kw["expire_on_commit"] is False
