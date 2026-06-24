from pathlib import Path
from unittest.mock import Mock

import pytest
from alembic.config import Config

from src import main
from src.config.constants import constants
from src.config.settings import settings
from src.migrations import commands
from src.storages.models import Base


class ConfigSpy:
    def __init__(self, file_: Path) -> None:
        self.file_ = file_
        self.options: dict[str, str] = {}

    def set_main_option(self, name: str, value: str) -> None:
        self.options[name] = value


class TestMigrationCommands:
    def test_migrate_configures_db_url_and_target_revision(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        created_configs: list[ConfigSpy] = []
        alembic_upgrade = Mock()

        def create_config(file_: Path) -> ConfigSpy:
            config = ConfigSpy(file_=file_)
            created_configs.append(config)
            return config

        monkeypatch.setattr(commands, "Config", create_config)
        monkeypatch.setattr(commands, "alembic_upgrade", alembic_upgrade)

        commands.migrate(
            revision="heads",
            db_url="postgresql+asyncpg://user:pass@localhost/showcase_test",
        )

        assert len(created_configs) == 1
        config = created_configs[0]
        assert config.file_ == constants.DIRS.SRC / "migrations" / "alembic.ini"
        assert (
            config.options["sqlalchemy.url"]
            == "postgresql+asyncpg://user:pass@localhost/showcase_test"
        )
        alembic_upgrade.assert_called_once_with(config=config, revision="heads")

    def test_downgrade_configures_db_url_and_target_revision(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        created_configs: list[ConfigSpy] = []
        alembic_downgrade = Mock()

        def create_config(file_: Path) -> ConfigSpy:
            config = ConfigSpy(file_=file_)
            created_configs.append(config)
            return config

        monkeypatch.setattr(commands, "Config", create_config)
        monkeypatch.setattr(commands, "alembic_downgrade", alembic_downgrade)

        commands.downgrade(
            revision="base",
            db_url="postgresql+asyncpg://user:pass@localhost/showcase_test",
        )

        assert len(created_configs) == 1
        config = created_configs[0]
        assert config.file_ == constants.DIRS.SRC / "migrations" / "alembic.ini"
        assert (
            config.options["sqlalchemy.url"]
            == "postgresql+asyncpg://user:pass@localhost/showcase_test"
        )
        alembic_downgrade.assert_called_once_with(config=config, revision="base")


class TestModelsMetadata:
    def test_base_metadata_starts_without_business_tables(self) -> None:
        assert Base.metadata.tables == {}


class TestMainMigrations:
    def test_start_service_runs_migrations_before_app_start(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        calls: list[str] = []

        def migrate(revision: str, db_url: str) -> None:
            calls.append(f"migrate:{revision}:{db_url}")

        def create_app(*, lifespan: object) -> object:
            _ = lifespan
            calls.append("create_app")
            return object()

        def setup_dishka(*, container: object, app: object) -> None:
            _ = (container, app)
            calls.append("setup_dishka")

        def create_container() -> object:
            calls.append("create_container")
            return object()

        def uvicorn_run(*, app: object, host: str, port: int, access_log: bool) -> None:
            _ = (app, host, port, access_log)
            calls.append("uvicorn.run")

        monkeypatch.setattr(main, "migrate", migrate)
        monkeypatch.setattr(main, "create_app", create_app)
        monkeypatch.setattr(main, "setup_dishka", setup_dishka)
        monkeypatch.setattr(main, "create_container", create_container)
        monkeypatch.setattr("src.main.uvicorn.run", uvicorn_run)

        main.start_service()

        assert calls == [
            f"migrate:heads:{settings.DATABASE.URL.get_secret_value()}",
            "create_app",
            "create_container",
            "setup_dishka",
            "uvicorn.run",
        ]


class TestAlembicConfig:
    def test_alembic_config_file_exists(self) -> None:
        config = Config(constants.DIRS.SRC / "migrations" / "alembic.ini")

        assert config.config_file_name == str(constants.DIRS.SRC / "migrations" / "alembic.ini")
