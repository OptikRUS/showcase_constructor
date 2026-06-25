# Reference: Migrations

## Именование файлов миграций

Файлы миграций называются **без даты**: `0001_create_entities.py`, `0002_add_status.py`.

Формат `alembic.ini` по умолчанию (`%%(rev)s_%%(slug)s`) оставляется без изменений —
`process_revision_directives` в `env.py` автоматически назначает четырёхзначный числовой rev_id.

**Запрещено:** `20260512_0001_create_entities.py` — дата в имени файла не используется.

## Publication/public-read database invariants

Publication migrations encode concurrency guarantees in PostgreSQL, not only in
Python code. Use domain-specific names in real migrations, but keep these
invariants:

```python
def upgrade() -> None:
    op.create_table(
        "publication_counters",
        sa.Column("entity_id", sa.BigInteger(), nullable=False),
        sa.Column("next_version", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("entity_id", name="pk_publication_counters"),
    )
    op.create_table(
        "publication_snapshots",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("entity_id", sa.BigInteger(), nullable=False),
        sa.Column("version", sa.BigInteger(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_publication_snapshots"),
        sa.UniqueConstraint("entity_id", "version", name="uq_publication_snapshots_version"),
    )
    op.create_table(
        "active_publications",
        sa.Column("entity_id", sa.BigInteger(), nullable=False),
        sa.Column("snapshot_id", sa.BigInteger(), nullable=False),
        sa.Column("version", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("entity_id", name="pk_active_publications"),
    )
    op.create_table(
        "public_identifiers",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("public_id", sa.String(), nullable=False),
        sa.Column("entity_id", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_public_identifiers"),
        sa.UniqueConstraint("public_id", name="uq_public_identifiers_public_id"),
    )
    op.create_table(
        "route_bindings",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("canonical_host", sa.String(), nullable=False),
        sa.Column("canonical_path", sa.String(), nullable=False),
        sa.Column("entity_id", sa.BigInteger(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_route_bindings"),
    )
    op.create_index(
        "uq_route_bindings_active_host_path",
        "route_bindings",
        ["canonical_host", "canonical_path"],
        unique=True,
        postgresql_where=sa.text("active"),
    )
```

`publication_snapshots` is append-only; add new rows for new versions. Route
bindings store canonical host/path values and use a unique active binding index
so reuse attempts for the same or another entity fail through the database.
Audit/event tables for publication mutations belong in the same migration slice
as the mutation tables when the feature requires audit rollback with the same
Unit of Work.

## src/migrations/commands.py

```python
from alembic.command import downgrade as alembic_downgrade
from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config

from src.config.constants import constants


def migrate(revision: str, db_url: str) -> None:
    config = Config(constants.DIRS.SRC / "migrations" / "alembic.ini")
    config.set_main_option("sqlalchemy.url", db_url)
    alembic_upgrade(config=config, revision=revision)


def downgrade(revision: str, db_url: str) -> None:
    config = Config(constants.DIRS.SRC / "migrations" / "alembic.ini")
    config.set_main_option("sqlalchemy.url", db_url)
    alembic_downgrade(config=config, revision=revision)
```

Do not add unit tests for `commands.py` that mock Alembic internals. Migration command
behavior is verified through shared test fixtures and a storage-layer migration smoke test.

## src/migrations/env.py

```python
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


def process_revision_directives(
    context: MigrationContext,
    revision: RevisionType,
    directives: list[MigrationScript],
) -> None:
    _ = revision
    migration_script = directives[0]
    head_revision = context.get_current_revision()
    new_rev_id = int(head_revision) + 1 if head_revision else 1
    migration_script.rev_id = f"{new_rev_id:04}"


target_metadata = models.Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
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
```

## src/migrations/script.py.mako

```mako
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
```

## src/migrations/alembic.ini (ключевые параметры)

```ini
[alembic]
script_location = %(here)s
# file_template НЕ переопределяется — rev_id назначается через process_revision_directives
path_separator = os
prepend_sys_path = .
```
