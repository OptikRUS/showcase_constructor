import asyncio
from collections.abc import Iterable

from alembic import context
from alembic.operations.ops import MigrationScript
from alembic.runtime.migration import MigrationContext
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from src.config.settings import settings
from src.storages import models

RevisionType = str | Iterable[str | None] | Iterable[str]

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE.URL.get_secret_value())
target_metadata = models.Base.metadata


def process_revision_directives(
    migration_context: MigrationContext,
    revision: RevisionType,
    directives: list[MigrationScript],
) -> None:
    _ = revision
    migration_script = directives[0]
    head_revision = migration_context.get_current_revision()
    new_rev_id = int(head_revision) + 1 if head_revision else 1
    migration_script.rev_id = f"{new_rev_id:04}"


def run_migrations_offline() -> None:
    url = config.get_main_option(name="sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        process_revision_directives=process_revision_directives,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    engine = context.config.attributes.get("engine", None)
    connectable = engine or async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.StaticPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    if not engine:
        await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
