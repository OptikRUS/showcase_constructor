# Plan: PostgreSQL MVP Infrastructure

## Goal

Update the MVP decision records to match `docs/showcase-constructor-tz.md`, then
add the PostgreSQL infrastructure foundation: async SQLAlchemy/asyncpg
dependencies, Alembic layout, database settings, request-scoped `AsyncSession`
Unit of Work, and centralized test database/session fixtures without adding
business tables or business route implementations.

## Context

- Current task description resolved from the rendered `ralphex --plan` request:
  update `docs/decisions/*.md` so PostgreSQL is the durable MVP storage instead
  of in-memory product storage; custom head/body code is allowed in MVP only as
  frontend code for counters/pixels with no backend execution; public/admin route
  decisions unblock MVP routes; outdated route-exposure tests are updated only as
  decision/guardrail cleanup; then implement PostgreSQL infrastructure with
  SQLAlchemy async, asyncpg, Alembic, pydantic-settings, `AsyncSession` DI Unit of
  Work, migrations layout, and test DB/session fixtures.
- Root `AGENTS.md`, `/Users/kirillpydev/.codex/RTK.md`,
  `docs/plans/README.md`, `docs/references/examples/ralphex.md`,
  `docs/decisions/mvp-boundaries.md`, and
  `docs/decisions/admin-api-lifecycle.md` were read before writing this plan.
- `AGENTS.md` references `/Users/optikrus/.codex/RTK.md`, but that file is absent
  in this environment. The available RTK rule requires all shell commands to be
  prefixed with `rtk`.
- No nested `AGENTS.md` files were found under the repository.
- `README.md` is absent. Project rules come from `AGENTS.md`, `pyproject.toml`,
  `Makefile`, `docs/plans/README.md`, and `docs/references/examples/`.
- `Makefile` exposes `tests`, `tests-coverage`, `lint`, `types`, `fix`, and
  `quality`; validation commands for this plan use only the required
  `rtk make ...` commands below.
- Current `pyproject.toml` already has `pydantic-settings` and lacks SQLAlchemy,
  asyncpg, and Alembic. `uv.lock` exists and must be updated with dependency
  changes.
- `src/config/settings.py` already defines `AuthSettings` and top-level
  `Settings`; no database settings or filesystem constants exist yet.
- `src/di/container.py::create_container` currently builds only
  `FastapiProvider()`. There are no database providers.
- No `src/storages/` or `src/migrations/` package exists. Existing storage
  interface work is limited to `src/core/storages.py::AdminShowcaseStorage`.
- `src/api/app.py::create_app` includes only
  `src/api/routers.py::root_router`; feature routers must still be registered
  only in `src/api/routers.py`.
- Existing live routes are `GET /health` and protected
  `GET /api/v1/admin/auth/context`. Admin showcase and public storefront
  business routes are not implemented by this plan.
- `src/tests/conftest.py`, `src/tests/fixtures.py`,
  `src/tests/helpers/api.py`, and `src/tests/helpers/factory.py` are the current
  centralized test infrastructure.
- `src/tests/api/test_admin_showcase_lifecycle_routes.py` and
  `src/tests/api/test_public_config_routes.py` currently assert candidate routes
  stay unregistered without decisions. Those tests are stale after this plan's
  decision update and should be converted to guard only explicitly blocked
  methods/aliases or removed when they no longer guard a blocked contract.
- `docs/showcase-constructor-tz.md` already selects PostgreSQL as durable MVP
  storage and says in-memory storage is only acceptable for unit tests or test
  doubles.
- `docs/showcase-constructor-tz.md` allows custom `head` and `body` code as
  trusted partner frontend code for metrics, pixels, and external widgets, while
  forbidding backend execution and raw end-user PII handling through custom code.
- `docs/decisions/mvp-boundaries.md` and
  `docs/decisions/admin-api-lifecycle.md` still contain outdated in-memory,
  custom-code-deny, and route-blocking language that must be reconciled before
  infrastructure work.
- Context7 documentation was checked for SQLAlchemy and Alembic. SQLAlchemy
  `/websites/sqlalchemy_en_20` confirms PostgreSQL asyncpg uses
  `create_async_engine("postgresql+asyncpg://...")`, `async_sessionmaker`, and
  `AsyncSession` transaction context managers. Alembic
  `/websites/alembic_sqlalchemy` confirms the async migration pattern with
  `async_engine_from_config`, `connection.run_sync(do_run_migrations)`, and
  disposing the async engine after migrations.
- No local Docker Compose, test database service definition, or `.env` template
  was found. The implementation must use `DB_*` settings consistently and must
  not replace PostgreSQL integration with SQLite or mock-only tests.

## Product/Security Decisions

- Method auth matrix: `GET /health -> public`;
  `GET /api/v1/admin/auth/context -> MVP JWT bearer auth`; admin MVP constructor
  routes from `docs/showcase-constructor-tz.md` use the current admin context and
  are not public; public storefront `GET /api/v1/public/showcases/resolve` and
  `GET /api/v1/public/showcases/{public_id}` are public published-snapshot reads;
  public event ingestion routes are public write endpoints only for approved
  non-PII event payloads.
- Public read decision: public reads may return only published snapshot data and
  must not read draft state. Explicit public `HEAD` and app-defined `OPTIONS`
  behavior remains a guardrail decision in the docs; CORS middleware must not
  expose private resource existence.
- Protected methods: all admin create, list, get, patch, publish, unpublish,
  clone, archive, block, offer, preview, domain, and verification routes require
  the current admin context. Admin `HEAD` and `OPTIONS` are not business routes
  unless a later focused decision approves them.
- Public data: public responses may expose only approved published snapshot
  field groups, including frontend custom head/body code after publication.
  Draft data, service credentials, private analytics, owner/admin identifiers,
  tenant/account identifiers, internal database identifiers, and raw custom-code
  review metadata stay private.
- Identifier exposure: public storefront lookup uses an opaque public showcase
  id or approved host/path resolution. Internal PostgreSQL primary keys are not
  public identifiers. Authenticated admin ids may be returned only for owned
  admin resources under the admin response boundary.
- Custom code: MVP permits custom head/body content only as partner-controlled
  frontend runtime content for counters, pixels, and external widgets. The
  backend stores and publishes it as data, never executes it, never gives it
  server-side secrets/runtime access, and must not use it to collect raw
  end-user PII.
- Product decision required: exact business table design, admin lifecycle
  transition behavior, publish/unpublish semantics, analytics retention, custom
  domain activation, durable audit/outbox design, final external auth provider,
  and concrete public event schemas remain outside this infrastructure plan.

## Implementation Notes

- Existing settings pattern: `src/config/settings.py::AuthSettings` uses
  `BaseSettings`, `SettingsConfigDict`, and `SecretStr`.
- Existing config reference: `docs/references/examples/config.md` shows
  `DatabaseSettings` with `DB_` env prefix and a computed `URL: SecretStr`.
- Existing DI reference: `docs/references/examples/di.md` shows a
  `DatabaseProvider` that yields `AsyncSession`, commits after success, rolls
  back on exception, and registers providers in `src/di/container.py`.
- Existing migration reference: `docs/references/examples/migrations.md` shows
  `src/migrations/commands.py`, async `env.py`, `script.py.mako`, and
  `alembic.ini` under `src/migrations`.
- Existing test reference: `docs/references/examples/tests.md` keeps database
  fixtures in `src/tests/conftest.py`, fixture mixins in `src/tests/fixtures.py`,
  and DB helpers in `src/tests/helpers/storage.py`.
- Expected settings shape sketch:
  ```python
  # sketch only; inspect real files before implementation
  class DatabaseSettings(BaseSettings):
      PROTOCOL: str = "postgresql+asyncpg"
      HOST: str = "localhost"
      PORT: int = 5432
      USER: str = "postgres"
      PASSWORD: SecretStr = SecretStr("postgres")
      NAME: str = "showcase_constructor"

      model_config = SettingsConfigDict(env_prefix="DB_")

      @property
      def URL(self) -> SecretStr:
          return SecretStr(
              f"{self.PROTOCOL}://{self.USER}:{self.PASSWORD.get_secret_value()}"
              f"@{self.HOST}:{self.PORT}/{self.NAME}"
          )
  ```
- Expected session factory shape sketch:
  ```python
  # sketch only; inspect real files before implementation
  async_engine = create_async_engine(settings.DATABASE.URL.get_secret_value())
  async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False)
  ```
- Expected DI Unit of Work shape sketch:
  ```python
  # sketch only; inspect real files before implementation
  class DatabaseProvider(Provider):
      @provide(scope=Scope.REQUEST)
      async def get_db_session(self) -> AsyncIterator[AsyncSession]:
          async with async_session() as session:
              try:
                  yield session
                  await session.commit()
              except Exception:
                  await session.rollback()
                  raise
  ```
- Expected Alembic async shape sketch:
  ```python
  # sketch only; inspect real files and Context7 docs before implementation
  connectable = async_engine_from_config(
      config.get_section(config.config_ini_section, {}),
      prefix="sqlalchemy.",
      poolclass=pool.NullPool,
  )
  async with connectable.connect() as connection:
      await connection.run_sync(do_run_migrations)
  await connectable.dispose()
  ```
- Edge cases:
  - do not add business ORM tables before table/domain decisions are approved;
  - keep `session.commit()` and `session.begin()` out of storages and use cases;
  - migration smoke must be empty or infrastructure-only, not a hidden business
    table;
  - test fixtures must be centralized and must not create local app/container or
    session fixtures inside layer-specific test files;
  - no-auth API scenarios continue to use `self.no_auth_api`;
  - approved public/admin route decisions do not mean route implementation is
    part of this plan.

## Constraints

- Follow `AGENTS.md` and applicable project references.
- Use `rtk` for shell commands.
- Use existing project patterns over new abstractions.
- Do not implement business FastAPI routes, use cases, storages, ORM models, or
  business migrations in this plan.
- Do not add business tables. Use an empty Alembic revision for migration smoke
  unless a pure infrastructure table is explicitly required by Alembic itself.
- Do not use SQLite as a substitute for PostgreSQL infrastructure validation.
- Do not add `repositories` or `repos`; concrete persistence belongs under
  `src/storages`.
- DI-managed `AsyncSession` is the Unit of Work; storage and use case code must
  not call `session.commit()` or `session.begin()`.
- Apply TDD to persistence behavior and test infrastructure behavior.
- Each Task should be small enough to finish with green validation.

## Validation Commands

- `rtk make lint`
- `rtk make types`
- `rtk make tests`
- `rtk make quality`

## Tasks

### Task 1: Align MVP decision records with the PostgreSQL route and custom-code boundary

**Success Criteria:**

- `docs/decisions/mvp-boundaries.md` states PostgreSQL is the approved durable
  MVP storage for constructor data, drafts, published snapshots, domains, audit
  trail, and events.
- In-memory storage is described only as a unit-test/test-double option, not as
  the product MVP storage boundary.
- The custom-code section allows partner custom head/body frontend code for
  counters, pixels, and external widgets, while forbidding backend execution,
  server-side secret/runtime access, and raw end-user PII handling through
  custom code.
- Public and admin route decision sections unblock the MVP route classes from
  `docs/showcase-constructor-tz.md` without implementing them.
- `docs/decisions/admin-api-lifecycle.md` no longer contradicts the PostgreSQL
  durable storage decision or the protected admin route boundary.
- Remaining `product decision required` items are limited to business behavior
  outside this infrastructure task and have concrete reasons.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: `docs/decisions/mvp-boundaries.md` and
  `docs/decisions/admin-api-lifecycle.md`.
- Existing pattern: both files use explicit boundary tables and
  `product decision required` rows for unresolved behavior.
- Decision shape sketch: change stale `Approved in-memory MVP storage boundary`
  language to `Approved MVP boundary: PostgreSQL durable storage`, then add a
  note that in-memory implementations are allowed only in tests/test doubles.
- Route matrix sketch: protected admin methods require `AdminActorContext`;
  public storefront `GET` reads published snapshots; public events accept only
  approved non-PII event payloads.

**Actions:**

- [x] Update `docs/decisions/mvp-boundaries.md` with the PostgreSQL durable
  storage boundary, custom-code frontend boundary, and public/admin MVP route
  decision matrix.
- [x] Update `docs/decisions/admin-api-lifecycle.md` so protected admin route
  decisions and persistence language match the updated MVP boundary.
- [x] Verify the decision records contain no stale claim that in-memory storage
  is the product MVP persistence layer.
- [x] Verify the decision records do not approve backend execution of custom
  code or public exposure of internal database identifiers.
- [x] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 2: Clean stale route-exposure guard tests without adding business routes

**Success Criteria:**

- Tests no longer assert that MVP-approved public/admin route classes are
  blocked merely because no decision exists.
- Any remaining route-exposure tests guard only explicitly blocked behavior,
  such as admin `HEAD`/`OPTIONS`, an unapproved `unarchive` alias, or unsupported
  public methods that the decision records still reject.
- No FastAPI business route, router registration, use case, storage, or schema is
  added in this task.
- Focused route guard tests pass.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: `src/tests/api/test_admin_showcase_lifecycle_routes.py`,
  `src/tests/api/test_public_config_routes.py`, and possibly
  `src/tests/helpers/api.py` if helper names need to stop implying blocked
  public config decisions.
- Existing pattern: route exposure tests use `APIFixture` and `httpx2.codes`.
- Assertion sketch:
  ```python
  response = self.api.client.request(method="HEAD", url="/api/v1/showcases")
  assert response.status_code == codes.NOT_FOUND
  ```

**Actions:**

- [x] Update admin lifecycle route-exposure tests so they guard only methods or
  aliases still explicitly blocked by the updated decision records.
- [x] Update or remove the public config route-exposure test so it no longer
  blocks future implementation of approved public `GET` routes.
- [x] Run `rtk uv run pytest -vv -x src/tests/api/test_admin_showcase_lifecycle_routes.py`.
- [x] Run `rtk uv run pytest -vv -x src/tests/api/test_public_config_routes.py`.
- [x] Confirm the task changed only guardrail tests/helpers and added no
  business implementation.
- [x] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 3: Add SQLAlchemy async, asyncpg, and Alembic dependencies

**Success Criteria:**

- `pyproject.toml` includes SQLAlchemy async support, asyncpg, and Alembic as
  runtime dependencies with project-compatible version ranges.
- `uv.lock` is updated by `uv`, not edited manually.
- Ruff/mypy configuration accounts for generated Alembic migration files without
  weakening checks for application code.
- No source code imports unavailable dependency names after the lock update.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: `pyproject.toml` and `uv.lock`.
- Dependency command sketch:
  ```bash
  rtk uv add "sqlalchemy[asyncio]>=2.0.0,<3.0.0" "asyncpg>=0.30.0,<1.0.0" "alembic>=1.13.0,<2.0.0"
  ```
- Tooling sketch: keep the existing `pydantic.mypy` plugin; add Ruff
  per-file ignore `src/migrations/**/*.py = ["INP001"]` and mypy
  `exclude = ["src/migrations/"]` as shown in
  `docs/references/examples/pyproject.toml`.

**Actions:**

- [ ] Add SQLAlchemy async support, asyncpg, and Alembic with `rtk uv add`.
- [ ] Add the Ruff migration per-file ignore and mypy migration exclude from
  the implementation sketch.
- [ ] Run `rtk uv lock --check` after `uv add` completes.
- [ ] Run `rtk make lint`, `rtk make types`, and `rtk make tests`.
- [ ] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 4: Add database settings and async session factory

**Success Criteria:**

- `src/config/settings.py` exposes `settings.DATABASE` with `DB_`-prefixed
  settings and a computed `URL: SecretStr` using `postgresql+asyncpg` by default.
- `src/config/constants.py` exposes project directories needed by migration
  commands without embedding machine-specific paths.
- `src/storages/database.py` creates an async SQLAlchemy engine and
  `async_sessionmaker` using `settings.DATABASE.URL`.
- `src/storages/__init__.py` exists only as package infrastructure.
- Focused tests cover database URL construction and import-level session factory
  availability without connecting to the database.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: `src/config/settings.py`, `src/config/constants.py`,
  `src/storages/__init__.py`, `src/storages/database.py`, and
  `src/tests/config/test_database_settings.py`.
- Existing pattern: `src/config/settings.py::AuthSettings` already uses
  `BaseSettings`, `SettingsConfigDict`, and `SecretStr`.
- Test assertion sketch:
  ```python
  database = DatabaseSettings(
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
  ```

**Actions:**

- [ ] Add a focused failing settings test for `DatabaseSettings.URL`.
- [ ] Add database settings and filesystem constants using the existing
  pydantic-settings style.
- [ ] Add `src/storages/database.py` with `create_async_engine` and
  `async_sessionmaker(expire_on_commit=False)`.
- [ ] Run `rtk uv run pytest -vv -x src/tests/config/test_database_settings.py`.
- [ ] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 5: Add Alembic async migration layout and smoke revision

**Success Criteria:**

- `src/migrations/commands.py` exposes `migrate(revision, db_url)` and
  `downgrade(revision, db_url)` using `alembic.config.Config`.
- `src/migrations/env.py` uses the async Alembic pattern from Context7 and the
  local migration reference: `async_engine_from_config`,
  `connection.run_sync(do_run_migrations)`, and engine disposal.
- `src/migrations/alembic.ini`, `src/migrations/script.py.mako`, and
  `src/migrations/versions/` exist with numeric revision naming.
- `src/storages/models.py` defines only `Base` metadata for future models; no
  business tables are added.
- The first revision is an empty migration smoke revision, not a business schema.
- `src/main.py` can run `migrate(revision="heads", db_url=settings.DATABASE.URL.get_secret_value())`
  before starting the app.
- Focused migration command tests pass without requiring a live database.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: `src/migrations/commands.py`, `src/migrations/env.py`,
  `src/migrations/alembic.ini`, `src/migrations/script.py.mako`,
  `src/migrations/versions/0001_migration_smoke.py`,
  `src/storages/models.py`, `src/main.py`, and
  `src/tests/migrations/test_commands.py`.
- Existing pattern: `docs/references/examples/migrations.md` shows the local
  command and async `env.py` shape.
- Test assertion sketch:
  ```python
  migrate(revision="heads", db_url="postgresql+asyncpg://u:p@localhost/db")
  alembic_upgrade.assert_called_once()
  ```

**Actions:**

- [ ] Add failing tests for migration command configuration without connecting
  to PostgreSQL.
- [ ] Add `src/storages/models.py::Base` with no business ORM models.
- [ ] Add Alembic `commands.py`, `env.py`, `alembic.ini`, `script.py.mako`, and
  an empty `0001_migration_smoke.py` revision.
- [ ] Wire `src/main.py` to run migrations on service start through
  `src.migrations.commands.migrate`.
- [ ] Run `rtk uv run pytest -vv -x src/tests/migrations/test_commands.py`.
- [ ] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 6: Wire request-scoped AsyncSession as the DI Unit of Work

**Success Criteria:**

- `src/di/providers/database.py` provides request-scoped `AsyncSession`.
- The provider commits after a successful request-scope use and rolls back before
  re-raising on exceptions.
- `src/di/container.py::create_container` includes `FastapiProvider()` and
  `DatabaseProvider()` without removing existing FastAPI integration.
- No storage or use case calls `session.commit()` or `session.begin()`.
- Focused tests prove the provider commit/rollback behavior.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: `src/di/providers/database.py`, `src/di/providers/__init__.py`,
  `src/di/container.py`, and `src/tests/di/test_database_provider.py`.
- Existing pattern: `docs/references/examples/di.md` shows
  `DatabaseProvider.get_db_session()`.
- Test assertion sketch:
  ```python
  session = await container.get(AsyncSession)
  assert isinstance(session, AsyncSession)
  ```
- Provider-unit assertion sketch:
  ```python
  # sketch only; use the real provider shape after implementation
  await fake_session.commit.assert_awaited_once()
  await fake_session.rollback.assert_not_awaited()
  ```

**Actions:**

- [ ] Add a focused failing provider test for successful commit and exception
  rollback.
- [ ] Implement `DatabaseProvider` using the shared `async_session` factory.
- [ ] Register `DatabaseProvider()` in `src/di/container.py`.
- [ ] Verify `rtk rg -n "session\\.(commit|begin)\\(" src/core src/storages`
  finds no forbidden storage/use-case transaction calls.
- [ ] Run `rtk uv run pytest -vv -x src/tests/di/test_database_provider.py`.
- [ ] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 7: Add centralized PostgreSQL test fixtures and migration smoke coverage

**Success Criteria:**

- `src/tests/conftest.py` owns test database engine, migration setup, and
  `AsyncSession` fixture wiring; no layer-specific test file defines its own DB
  fixture.
- `src/tests/fixtures.py` exposes a `StorageFixture` for the shared DB helper.
- `src/tests/helpers/storage.py` contains DB helper methods for infrastructure
  readback without business-table assumptions.
- Migration smoke coverage upgrades to heads and downgrades to base against the
  configured PostgreSQL test database.
- The fixture uses `NullPool` or another test-safe pooling strategy and disposes
  the engine after the test session.
- `rtk make quality` exits successfully with a reachable PostgreSQL test
  database configured through `DB_*` settings.

**Implementation Sketch:**

- Likely files: `src/tests/conftest.py`, `src/tests/fixtures.py`,
  `src/tests/helpers/storage.py`, and
  `src/tests/migrations/test_migrations_smoke.py`.
- Existing pattern: `docs/references/examples/tests.md` keeps migrations,
  engine, session, and storage helper fixtures centralized.
- Migration smoke assertion sketch:
  ```python
  result = await session.execute(text("select version_num from alembic_version"))
  assert result.scalar_one() == "0001"
  ```

**Actions:**

- [ ] Add a failing migration smoke test that uses only Alembic metadata/version
  state and no business tables.
- [ ] Add centralized test engine, migration setup, and `AsyncSession` fixtures
  in `src/tests/conftest.py`.
- [ ] Add `StorageFixture` and `src/tests/helpers/storage.py` for shared DB
  readback needed by the smoke test and future storage tests.
- [ ] Run `rtk uv run pytest -vv -x src/tests/migrations/test_migrations_smoke.py`
  with PostgreSQL `DB_*` settings configured.
- [ ] Run `rtk make quality`, fix all failures, and repeat until successful.
