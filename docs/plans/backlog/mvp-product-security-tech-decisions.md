# Plan: MVP Product/Security/Tech Decisions

## Goal

Зафиксировать MVP-границы конструктора витрин и блокирующие Product/Security/Tech
Decisions до проектирования feature plans: auth model для admin API, persistence
choice, public identifier exposure, domain verification method, audit/event
durability и custom code permissions. Бизнес-код, runtime-конфигурация, persistence
и API endpoints в рамках этого плана не реализуются.

## Context

- Текущий task description взят из rendered `ralphex --plan` request:
  `Зафиксируй MVP-границы и блокирующие Product/Security/Tech Decisions для конструктора витрин: auth model для admin API, persistence choice, public identifier exposure, domain verification method, audit/event durability, custom code permissions. Не реализуй бизнес-код; создай decision-first план, который разблокирует следующие feature plans.`
- Root `AGENTS.md` прочитан; других nested `AGENTS.md` в репозитории нет.
- `AGENTS.md` ссылается на `/Users/optikrus/.codex/RTK.md`, но этот файл отсутствует в текущем окружении. Доступный `/Users/kirillpydev/.codex/RTK.md` требует префикс `rtk` для shell-команд.
- `README.md` в репозитории отсутствует; локальные правила берутся из `AGENTS.md`,
  `pyproject.toml`, `Makefile`, `docs/plans/README.md` и
  `docs/references/examples/ralphex.md`.
- Текущий код минимален: `src/api/app.py::create_app` отключает docs/openapi/redoc и
  подключает только `src/api/routers.py::root_router`; `src/api/common/endpoints.py::health`
  является единственным endpoint.
- `src/di/container.py::create_container` сейчас собирает только `FastapiProvider()`;
  доменных providers, `src/core`, `src/storages`, `src/config` и `migrations` нет.
- Тестовая инфраструктура уже централизована: `src/tests/conftest.py`, `src/tests/fixtures.py::APIFixture`,
  `src/tests/helpers/api.py::APIHelper`, `src/tests/api/test_health.py::TestHealthAPI`.
- `Makefile` содержит реальные targets `tests`, `tests-coverage`, `lint`, `types`, `fix`,
  `quality`; для плановой валидации используются только project-required команды ниже.
- Этот план не требует новых dependencies, runtime settings, database layer, Alembic migrations
  или изменений app code. Все будущие feature plans должны ссылаться на зафиксированные
  решения или явно блокироваться как `product decision required`.

## Product/Security Decisions

- Method auth matrix: current `GET /health -> public`; future admin API methods are
  `product decision required` until the admin auth model and per-method permissions are
  explicitly approved.
- Public read decision: current public read surface is only `GET /health`; public
  storefront `GET`/`HEAD`/`OPTIONS` routes are `product decision required` until response
  fields and identifier exposure are approved.
- Protected methods: future admin `POST`/`PUT`/`PATCH`/`DELETE` and any management `GET`
  are `product decision required`; do not implement protected routes before choosing token,
  session, or another explicit admin auth model.
- Public data: future public response fields for showcases, domains, owners, themes, pages,
  assets, custom code metadata and verification status are `product decision required`.
- Identifier exposure: internal database IDs, admin emails, usernames, profile identifiers
  and tenant/account identifiers must not be exposed publicly unless the decision record
  explicitly approves the field and rationale.
- Product decision required: choose admin API auth model; persistence backend and migration
  boundary; public identifier model; domain verification method; required audit/event
  durability; custom code permission/sandbox policy; MVP in/out scope for constructor,
  publishing, custom domains, analytics and billing.

## Constraints

- Follow `AGENTS.md`, `docs/plans/README.md` and `docs/references/examples/ralphex.md`.
- Save this plan in `docs/plans/backlog/`; do not create files under
  `docs/superpowers/plans/`.
- Do not implement business code, FastAPI endpoints, DI providers, storages, settings or
  migrations in this decision-first plan.
- Use existing project patterns when later feature plans introduce code:
  `src/api/routers.py::root_router`, `DishkaRoute` for DI endpoints, `src/di/container.py`,
  centralized fixtures and helpers under `src/tests/`.
- Do not add dependencies unless a later implementation plan explicitly updates both
  `pyproject.toml` and `uv.lock`.
- Apply TDD to future behavior changes; documentation-only decision work does not require
  artificial RED/GREEN tests.
- Every unresolved public/auth/identifier/data exposure point must stay marked
  `product decision required`; do not choose defaults implicitly.

## Validation Commands

- `rtk make lint`
- `rtk make types`
- `rtk make tests`
- `rtk make quality`

## Tasks

### Task 1: Create MVP scope decision record

**Success Criteria:**

- `docs/decisions/mvp-boundaries.md` exists as a new decision record under the verified
  `docs/` tree.
- The decision record states MVP in-scope and out-of-scope boundaries for constructor,
  showcase publishing, custom domains, analytics, billing, admin API and public storefront.
- Any boundary that is not explicitly confirmed is recorded as `product decision required`,
  not converted into an implementation assumption.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: create `docs/decisions/mvp-boundaries.md`.
- Existing pattern: RALPHEX plan governance in `docs/plans/README.md` and
  `docs/references/examples/ralphex.md`.
- Document shape sketch (not final content):
  ```markdown
  # MVP Boundaries

  ## Scope

  - In scope: ...
  - Out of scope: ...

  ## Blocking Decisions

  - Product decision required: ...
  ```

**Actions:**

- [x] Create `docs/decisions/mvp-boundaries.md` with a concise MVP scope section.
- [x] Mark unconfirmed scope points exactly as `product decision required`.
- [x] Add a short "Blocked Feature Plans" section listing which later feature plans must wait for the decisions.
- [x] Run `rtk rg -n "product decision required|Blocked Feature Plans|In scope|Out of scope" docs/decisions/mvp-boundaries.md`.
- [x] Run `rtk make quality`, fix documentation-related failures if any, and repeat until successful.

### Task 2: Record admin API auth and method exposure decisions

**Success Criteria:**

- The decision record defines the intended admin API auth model or explicitly marks it
  `product decision required`.
- The decision record contains a method auth matrix for admin routes before any admin
  endpoint implementation plan exists.
- Public `GET`/`HEAD`/`OPTIONS` behavior and protected management methods are stated
  without inferring defaults.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: modify `docs/decisions/mvp-boundaries.md`.
- Existing pattern for later code: future admin endpoints must compose through
  `src/api/routers.py::root_router` and use centralized test helpers like
  `src/tests/fixtures.py::APIFixture`.
- Matrix sketch (not final content):
  ```markdown
  ## Admin API Auth

  | Surface | Method | Auth | Status |
  | --- | --- | --- | --- |
  | Admin API | GET | product decision required | blocked |
  | Admin API | POST/PATCH/DELETE | product decision required | blocked |
  ```

**Actions:**

- [x] Add an "Admin API Auth" section with the selected auth model or `product decision required`.
- [x] Add a method auth matrix covering admin read and write methods.
- [x] State whether any admin `GET`, `HEAD` or `OPTIONS` route may be public; if not confirmed, keep it blocked.
- [x] Run `rtk rg -n "Admin API Auth|Method|GET|POST|PATCH|DELETE|product decision required" docs/decisions/mvp-boundaries.md`.
- [x] Run `rtk make quality`, fix documentation-related failures if any, and repeat until successful.

### Task 3: Record public data and identifier exposure decisions

**Success Criteria:**

- The decision record states which public storefront data may be exposed, or marks each
  unconfirmed class of data as `product decision required`.
- Internal IDs, admin emails, usernames, profile identifiers and tenant/account identifiers
  are explicitly classified as not publicly exposed unless a decision approves them.
- Future feature plans can tell whether to use public slugs, opaque IDs, custom domains,
  or another approved public identifier scheme.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: modify `docs/decisions/mvp-boundaries.md`.
- Existing pattern for later code: public API schemas should be boundary models under
  `src/api/<domain>/schemas.py` only after this decision approves response fields.
- Exposure table sketch (not final content):
  ```markdown
  ## Public Data And Identifiers

  | Field class | Public exposure | Rationale |
  | --- | --- | --- |
  | Internal database IDs | product decision required | blocked |
  | Public showcase identifier | product decision required | blocked |
  ```

**Actions:**

- [x] Add a "Public Data And Identifiers" section.
- [x] Classify public showcase identifiers, internal IDs, owner/admin identifiers and domain names.
- [x] Record the exposure rationale for each approved field, or mark it `product decision required`.
- [x] Run `rtk rg -n "Public Data And Identifiers|Internal database IDs|identifier|product decision required" docs/decisions/mvp-boundaries.md`.
- [x] Run `rtk make quality`, fix documentation-related failures if any, and repeat until successful.

### Task 4: Record persistence and migration boundary decisions

**Success Criteria:**

- The decision record states the MVP persistence choice or marks it `product decision required`.
- The record states whether the first persistence feature plan may add `src/config`,
  `src/storages`, `src/core/storages.py` and `migrations`, or must remain in-memory.
- The record preserves project rules: storage layer is `storages`, transactions belong in
  DI providers, and no `repositories` layer is introduced.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: modify `docs/decisions/mvp-boundaries.md`.
- Existing references: `docs/references/examples/storages.md`, `docs/references/examples/di.md`,
  `docs/references/examples/config.md`, `docs/references/examples/migrations.md`.
- Boundary sketch (not final content):
  ```markdown
  ## Persistence

  - MVP backend: product decision required
  - May introduce DB config: product decision required
  - Transaction boundary: DI provider, not storage/use case
  ```

**Actions:**

- [x] Add a "Persistence" section with backend choice, migration boundary and config boundary.
- [x] State whether future plans may introduce `src/config`, `src/storages` and `migrations`.
- [x] Record the storage naming and transaction boundary constraints from `AGENTS.md`.
- [x] Run `rtk rg -n "Persistence|storages|migrations|transaction|product decision required" docs/decisions/mvp-boundaries.md`.
- [x] Run `rtk make quality`, fix documentation-related failures if any, and repeat until successful.

### Task 5: Record domain verification and audit/event durability decisions

**Success Criteria:**

- The decision record states the MVP domain verification method or marks it
  `product decision required`.
- The record states audit/event durability requirements for admin changes, publishing,
  domain verification and custom code changes, or marks them `product decision required`.
- Future feature plans can tell whether events are best-effort logs, durable DB records,
  outbox events, or another explicitly approved mechanism.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: modify `docs/decisions/mvp-boundaries.md`.
- Existing constraint: no current event, client, service, storage, config or migration layer
  exists; later plans must introduce only the layers required by the chosen durability model.
- Decision sketch (not final content):
  ```markdown
  ## Domain Verification

  - Method: product decision required

  ## Audit And Events

  - Durability: product decision required
  - Required audited actions: product decision required
  ```

**Actions:**

- [ ] Add a "Domain Verification" section with approved method or `product decision required`.
- [ ] Add an "Audit And Events" section with durability level and audited action classes.
- [ ] Link each unresolved durability or verification question to the feature plan it blocks.
- [ ] Run `rtk rg -n "Domain Verification|Audit And Events|durability|product decision required" docs/decisions/mvp-boundaries.md`.
- [ ] Run `rtk make quality`, fix documentation-related failures if any, and repeat until successful.

### Task 6: Record custom code permission decisions

**Success Criteria:**

- The decision record states whether MVP allows user-supplied custom code, CSS, HTML,
  JavaScript, embeds or server-side logic, or marks each category `product decision required`.
- The record states permission, sanitization, sandboxing and review requirements before any
  custom-code feature plan can implement execution or rendering.
- Security-sensitive defaults are not inferred by the executor; unresolved points remain
  explicitly blocked.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: modify `docs/decisions/mvp-boundaries.md`.
- Existing constraint: the current project has no rendering, client, storage or security
  policy layer; future plans must not add one until this decision is explicit.
- Permission sketch (not final content):
  ```markdown
  ## Custom Code Permissions

  | Capability | MVP permission | Required controls |
  | --- | --- | --- |
  | Custom CSS | product decision required | blocked |
  | Custom JavaScript | product decision required | blocked |
  | Server-side custom code | product decision required | blocked |
  ```

**Actions:**

- [ ] Add a "Custom Code Permissions" section.
- [ ] Classify CSS, HTML, JavaScript, external embeds and server-side code separately.
- [ ] Record required controls for each allowed capability, or mark it `product decision required`.
- [ ] Run `rtk rg -n "Custom Code Permissions|CSS|JavaScript|server-side|product decision required" docs/decisions/mvp-boundaries.md`.
- [ ] Run `rtk make quality`, fix documentation-related failures if any, and repeat until successful.
