# Plan: Custom Code Preview Publish Public Read Path

## Goal

Implement the approved MVP path for owner-controlled custom `head`/`body`
frontend code, draft preview, publish/unpublish snapshots, and public
published-snapshot reads while preserving the private draft/admin boundary and
leaving unresolved host/path routing and cache-backend details explicit.

## Context

- Current task description was resolved from the rendered `ralphex --plan`
  request: implement custom head/body code, preview, publish/unpublish snapshots,
  and public config/resolve APIs from `docs/showcase-constructor-tz.md`.
- Root `AGENTS.md`, `/Users/kirillpydev/.codex/RTK.md`,
  `docs/plans/README.md`, `docs/references/examples/ralphex.md`,
  `docs/decisions/mvp-boundaries.md`,
  `docs/decisions/admin-api-lifecycle.md`,
  `docs/decisions/draft-constructor-editing.md`,
  `docs/showcase-constructor-tz.md`, and the relevant API/core/storage/DI/test
  references were read before writing this plan.
- `AGENTS.md` references `/Users/optikrus/.codex/RTK.md`, but that file is absent
  in this environment. The available RTK rule requires all shell commands to use
  the `rtk` prefix.
- No nested `AGENTS.md` files were found under the repository. Root `README.md`
  is absent.
- `Makefile` exposes `tests`, `tests-coverage`, `lint`, `types`, `fix`, and
  `quality`; narrow behavior checks should use the existing project pattern
  `rtk uv run pytest -vv -x ...`.
- Current protected showcase routes live in
  `src/api/showcases/endpoints.py` with `DishkaRoute`, `JwtUserDeps`,
  `AdminActorContext`, and one use case per endpoint.
- `src/api/showcases/schemas.py::AdminShowcaseDraftPatchRequest` currently
  supports design/text/banner/fallback draft settings but not custom
  `head`/`body` code or custom-code warning fields.
- `src/core/showcases/schemas.py` contains draft settings, block, and offer
  schemas. `src/core/showcases/use_cases.py` enforces owner checks before draft
  mutations. `src/core/storages.py::AdminShowcaseStorage` is the existing core
  storage interface.
- `src/storages/models.py` currently has `showcases`, `draft_blocks`, and
  `draft_offers`. `showcases.published_snapshot` is a mutable JSONB column, and
  there is no immutable published snapshot table, publication version field,
  public id binding, route binding, or audit table yet.
- `src/migrations/versions/0002_create_draft_constructor_tables.py` is the latest
  migration. New persistence work should use a focused `0003_*.py` Alembic
  migration and update `src/tests/storages/test_database_migrations.py`.
- `src/api/public_config/schemas.py::PublicConfigResponse` and
  `src/core/public_config/schemas.py::PublishedPublicConfigSnapshot` already
  model the current widgetmarket-compatible public shape and reject
  draft/private fields in tests, but they do not yet include published custom
  code fields.
- `src/tests/fixtures.py::APIFixture`, `FactoryFixture`, and `StorageFixture`,
  `src/tests/helpers/api.py::APIHelper`,
  `src/tests/helpers/factory.py::FactoryHelper`, and
  `src/tests/helpers/storage.py::StorageHelper` are the shared test surfaces to
  extend.
- `docs/decisions/mvp-boundaries.md` approves partner-controlled frontend
  `head`/`body` code, protected owner-scoped preview/publish route classes,
  public published-snapshot reads, PostgreSQL durable storage, and safe audit
  records for approved mutations.
- `docs/decisions/mvp-boundaries.md` still leaves exact public cache backend,
  host/path binding source, custom-domain activation, final audit retention,
  transactional outbox, and broader analytics/event behavior as
  `product decision required`.
- This task requires persistence and Alembic changes, but it should not require
  new third-party dependencies or new runtime configuration.

## Product/Security Decisions

- Method auth matrix:
  `PATCH /api/v1/showcases/{id} -> token/session auth` for custom code draft
  edits through the existing current admin JWT context;
  `POST /api/v1/showcases/{id}/preview -> token/session auth`;
  `POST /api/v1/showcases/{id}/publish -> token/session auth`;
  `POST /api/v1/showcases/{id}/unpublish -> token/session auth`;
  `GET /api/v1/public/showcases/{public_id} -> public`;
  `GET /api/v1/public/showcases/resolve?host=...&path=... -> public only for
  explicit published route bindings`.
- Public read decision: only the two public `GET` routes above may be registered
  by this plan. Public reads must use an active published snapshot only, return
  `404` for missing/draft/unpublished/archived resources, and must not read
  draft tables directly.
- Public `HEAD` and `OPTIONS`: no app-defined public `HEAD` or `OPTIONS`
  business routes are approved by this plan. If framework or middleware behavior
  exists, it must not expose draft/private resource existence or additional
  public fields.
- Protected methods: every admin method touched by this plan requires
  `src.api.auth.deps.JwtUserDeps`, constructs the already validated
  `AdminActorContext`, delegates to exactly one use case, and performs owner
  checks in core before mutation, preview, publication, or audit append.
- Public data: public responses may expose only the approved published snapshot
  field groups already represented by `PublicConfigResponse`, plus published
  frontend custom `head`/`body` code after publication. Draft custom code,
  custom-code review metadata, audit metadata, owner/admin identifiers, internal
  database ids, service settings, private analytics, raw PII, and server-side
  custom-code metadata are not public data.
- Identifier exposure: public `id` and `{public_id}` must be opaque public
  showcase ids, not internal database ids, admin showcase ids, owner ids,
  partner ids, emails, usernames, tenant/account ids, slugs, custom-domain names,
  or reversible values. Owned admin `showcase_id` remains protected admin data.
- Custom code execution boundary: the backend stores, previews, snapshots, and
  serializes custom `head`/`body` code as frontend data only. It must not execute
  custom code, provide server-side secrets/runtime/filesystem/network access, or
  process raw end-user PII through custom code.
- Audit boundary: custom-code edits, publish, and unpublish must append durable
  PostgreSQL audit records with actor attribution and safe metadata after owner
  checks. Audit records must not store raw custom-code contents, full draft
  payloads, service credentials, secrets, or raw PII.
- Product decision required: exact host/path binding source and custom-domain
  activation remain unresolved. This plan may support lookup through explicit
  published route binding rows, but must not infer production host/path routing
  from `trackingDomain`, arbitrary draft settings, or unverified domains.
- Product decision required: exact public cache backend and distributed
  invalidation semantics remain unresolved. This plan may add a cache
  invalidation boundary/no-op adapter and tests that it is called, but must not
  introduce a cache dependency or runtime config without a later decision.
- Product decision required: audit retention, transactional outbox, external
  event streams, idempotency, analytics visibility, and billing relevance remain
  unresolved. This plan implements only the safe durable audit records required
  for the requested mutations.

## Implementation Notes

- Existing API pattern: add protected admin route handlers in
  `src/api/showcases/endpoints.py` and public route handlers in a focused
  `src/api/public_config/endpoints.py`; register routers only through
  `src/api/routers.py::root_router`.
- Existing schema pattern: use `src/api/boundary.py::BoundaryModel` and
  `from_domain(...)` conversion methods. Keep the existing camelCase public JSON
  aliases and the special snake_case
  `is_need_to_send_offers_display_and_positions` flag.
- Existing core pattern: keep business rules in
  `src/core/showcases/use_cases.py` and projection/public config logic in
  `src/core/public_config/` or a similarly focused core module. Endpoints should
  not assemble snapshots or apply business validation.
- Existing storage pattern: extend `src/core/storages.py::AdminShowcaseStorage`
  or add narrow public/audit storage interfaces only when the use case requires
  them. Concrete SQLAlchemy implementations belong under `src/storages/` and
  must not call `session.commit()` or `session.begin()`.
- Expected admin endpoint sketch:
  ```python
  # sketch only; inspect real files before implementation
  @router.post(path="/{showcase_id}/publish", status_code=status.HTTP_200_OK)
  async def publish_showcase(
      showcase_id: str,
      user: JwtUserDeps,
      use_case: FromDishka[PublishAdminShowcaseUseCase],
  ) -> AdminPublishedShowcaseResponse:
      context = AdminActorContext(user_id=user.user_id, partner_id=user.partner_id)
      result = await use_case.execute(showcase_id=showcase_id, context=context)
      return AdminPublishedShowcaseResponse.from_domain(result=result)
  ```
- Expected public endpoint sketch:
  ```python
  # sketch only; inspect real files before implementation
  @router.get(path="/{public_id}", status_code=status.HTTP_200_OK)
  async def get_public_showcase(
      public_id: str,
      use_case: FromDishka[GetPublishedPublicConfigUseCase],
  ) -> PublicConfigResponse:
      snapshot = await use_case.execute(public_id=public_id)
      return PublicConfigResponse.from_domain(snapshot=snapshot)
  ```
- Expected preview response sketch:
  ```python
  # sketch only; inspect real files before implementation
  response = self.api.preview_admin_showcase(
      showcase_id="showcase-1",
      json={"mode": "mobile"},
  )
  assert response.json()["preview"] is True
  assert response.json()["mode"] == "mobile"
  assert response.json()["config"]["id"].startswith("preview-")
  ```
- Expected audit assertion sketch:
  ```python
  records = await self.storage_helper.list_showcase_audit_records(showcase_id="showcase-1")
  assert records[0].action == "custom_code_updated"
  assert "customHeadCode" not in records[0].metadata
  ```
- Edge cases:
  - no-auth admin API scenarios use `self.no_auth_api` in separate
    `Test*NoAuthAPI` classes;
  - foreign resources return `403`, missing resources return `404`, and failed
    `401`/`403`/`404` paths do not mutate state or append audit records;
  - blank or missing JWT subject fields remain rejected in `src/api/auth/*`, not
    in core context factories;
  - missing patch fields mean no change, while explicit `null` clears nullable
    custom code fields if the request schema permits it;
  - preview uses draft data and may include custom code as inert strings/HTML
    output, but must not update published snapshot tables or active public
    visibility;
  - publish excludes disabled offers and hidden offer fields from public
    projection, copies custom code only into the new snapshot, and never exposes
    draft/internal/admin fields publicly;
  - public reads must not mutate counters, analytics, audit records, cache, or
    storage state.

## Constraints

- Follow `AGENTS.md` and applicable nested instructions.
- Use existing project patterns and inspect real files again before editing.
- Use `rtk` for shell commands.
- Do not change architecture without necessity.
- Do not add new dependencies unless the plan is amended to update both
  `pyproject.toml` and `uv.lock`.
- Do not add new runtime configuration unless a later cache/domain decision
  requires it.
- Do not create standalone `src/tests/config/`, `src/tests/di/`, or
  `src/tests/migrations/` directories for infrastructure mechanics.
- Do not use `repositories` or `repos`; the persistence layer is `storages`.
- Do not call `session.commit()` or `session.begin()` in storage or use case
  code; the DI database provider owns the Unit of Work.
- Do not expose draft data through public APIs.
- Do not implement custom-domain activation, DNS verification, analytics event
  ingestion, billing behavior, server-side custom code, raw end-user PII
  collection, or external cache backends in this plan.
- Apply TDD to behavior changes.
- Each Task should be one cohesive vertical milestone that can finish with green
  validation in one RALPHEX iteration.

## Validation Commands

- `rtk make lint`
- `rtk make types`
- `rtk make tests`
- `rtk make quality`

## Tasks

### Task 1: Add publication, public-id, route-binding, and audit persistence foundation

**Success Criteria:**

- PostgreSQL schema supports durable public id binding, active publication
  state, immutable published snapshot rows, explicit host/path route binding
  rows for already-approved published routes, and safe audit records.
- Existing draft storage behavior remains intact, and current tests for draft
  settings, blocks, offers, migrations, and public config schemas keep passing.
- `src/tests/storages/test_database_migrations.py` proves the new migration is
  the head revision and exposes expected tables/columns without creating
  standalone migration test directories.
- Storage/helper tests prove immutable snapshot rows retain versioned payload,
  actor/time metadata, and public ids without exposing internal primary keys.
- Audit helper/storage tests prove audit metadata excludes raw custom-code
  contents, full snapshots, secrets, and raw PII.
- The narrowest relevant checks include
  `rtk uv run pytest -vv -x src/tests/storages/test_database_migrations.py::TestDatabaseMigrations::test_upgrades_to_head_revision`
  and focused storage tests added for snapshot/audit persistence.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: `src/migrations/versions/0003_create_publication_snapshot_tables.py`,
  `src/storages/models.py`, `src/storages/showcases.py`,
  `src/core/showcases/schemas.py`, `src/core/storages.py`,
  `src/tests/helpers/storage.py`, `src/tests/storages/test_database_migrations.py`,
  and `src/tests/storages/test_admin_showcase_storage.py`.
- Existing pattern: `src/migrations/versions/0002_create_draft_constructor_tables.py`
  names constraints explicitly; `src/storages/showcases.py` returns domain
  schemas and raises core exceptions when rows are missing.
- Code shape sketch (not final code): add a published snapshots table with
  `public_id`, `version`, immutable `snapshot` JSONB, `created_by_user_id`,
  `created_by_partner_id`, `created_at`; add a safe audit table with `action`
  and JSONB `metadata`; add route binding storage for explicit `host`/`path` to
  active public id.
- Assertion sketch (not final code): create a showcase, insert a snapshot and
  audit record through storage, read them back through helpers, and assert
  internal ids and raw custom code are absent from returned domain objects.

**Actions:**

- [x] Add or update focused migration/storage tests for publication metadata,
  immutable snapshots, route bindings, and audit records.
- [x] Run the narrowest relevant storage/migration tests and confirm they fail
  for the expected missing tables, columns, storage methods, or helpers.
- [x] Make the minimal migration, model, storage, and helper changes required
  for the tests to pass.
- [x] Re-run the focused migration/storage tests and confirm they pass.
- [x] Perform only necessary safe refactoring and re-run the focused tests.
- [x] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 2: Add owner-only custom head/body draft edit with admin warning and audit

**Success Criteria:**

- `PATCH /api/v1/showcases/{id}` accepts owner-only custom `head` and `body`
  frontend code fields as draft data and returns an admin-visible warning when
  either custom-code field is present.
- Custom code is stored in draft only and does not change any active published
  snapshot or public route visibility.
- Successful custom-code changes append one safe audit record after the owner
  check; failed no-auth, foreign-owner, and missing-resource paths do not mutate
  draft state and do not append audit records.
- Admin response and storage tests prove raw custom-code content is not written
  into audit metadata.
- Backend code never executes, imports, evaluates, fetches, or parses custom
  scripts as executable server behavior; it treats custom code as string data.
- The narrowest relevant checks include
  `rtk uv run pytest -vv -x src/tests/api/test_admin_showcase_draft_settings.py::TestAdminShowcaseDraftSettingsAPI::test_patches_custom_head_body_code_with_warning_and_audit`
  and focused core/storage tests for the custom-code use case.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: `src/api/showcases/schemas.py`,
  `src/api/showcases/endpoints.py`, `src/core/showcases/schemas.py`,
  `src/core/showcases/use_cases.py`, `src/core/storages.py`,
  `src/storages/showcases.py`, `src/di/providers/showcases.py`,
  `src/tests/helpers/api.py`, `src/tests/helpers/storage.py`,
  `src/tests/api/test_admin_showcase_draft_settings.py`,
  `src/tests/core/showcases/test_update_admin_showcase_use_case.py`, and
  `src/tests/storages/test_admin_showcase_storage.py`.
- Existing pattern: draft settings patch already merges JSONB values in
  `DatabaseAdminShowcaseStorage.update_draft_settings`; extend that path rather
  than adding a parallel endpoint for the same draft aggregate.
- Code shape sketch (not final code): add `custom_head_code` and
  `custom_body_code` nullable fields to `AdminShowcaseDraftPatchRequest`, include
  them in `AdminShowcaseDraftSettingsPatchParams`, and add an admin warning
  response field such as `customCodeWarning` or `warnings.customCode` after
  checking the preferred local boundary shape.
- Assertion sketch (not final code): patch both custom code fields, assert
  response includes camelCase custom fields and warning text, assert
  `published_snapshot` is unchanged, and assert the audit metadata lists changed
  locations without raw code content.

**Actions:**

- [ ] Add or update focused API/core/storage tests for owner custom-code draft
  edits, warning response, audit append, no-auth, foreign-owner, missing
  resource, and published-snapshot separation.
- [ ] Run the narrowest relevant tests and confirm they fail for the expected
  missing schema fields, warning, audit, or storage behavior.
- [ ] Make the minimal production changes required for the tests to pass.
- [ ] Re-run the focused tests and confirm they pass.
- [ ] Perform only necessary safe refactoring and re-run the focused tests.
- [ ] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 3: Build draft-to-public projection and protected preview endpoint

**Success Criteria:**

- `POST /api/v1/showcases/{id}/preview` is protected by current admin JWT
  context, owner-scoped, and supports `desktop` and `mobile` modes.
- Preview builds a production-like public config from draft settings, visible
  draft blocks, enabled draft offers, visible offer fields, fallback settings,
  and draft custom `head`/`body` code without reading or mutating the active
  published snapshot.
- Preview response is explicitly marked as preview and includes the requested
  mode. If HTML is returned, the HTML is marked preview and contains custom code
  only as frontend output, not backend-executed code.
- Preview returns `401` for no auth, `403` for foreign-owner resources, `404` for
  missing resources, and validation errors for unsupported mode values.
- Public routes cannot access draft preview data or draft custom code.
- The narrowest relevant checks include
  `rtk uv run pytest -vv -x src/tests/api/test_admin_showcase_preview.py::TestAdminShowcasePreviewAPI::test_builds_mobile_preview_from_draft_without_publishing`
  and focused core projection tests.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: `src/api/showcases/endpoints.py`,
  `src/api/showcases/schemas.py`, `src/core/showcases/use_cases.py`,
  `src/core/public_config/schemas.py`, `src/api/public_config/schemas.py`,
  `src/core/storages.py`, `src/storages/showcases.py`,
  `src/di/providers/showcases.py`, `src/tests/helpers/api.py`,
  `src/tests/helpers/factory.py`, `src/tests/helpers/storage.py`,
  `src/tests/api/test_admin_showcase_preview.py`, and focused core tests under
  `src/tests/core/showcases/` or `src/tests/core/public_config/`.
- Existing pattern: owner checks belong in use cases; API boundary schemas
  perform request/response conversion only.
- Code shape sketch (not final code): add a preview use case that reads the
  draft, blocks, and offers through storage, calls a pure draft-to-public
  projection helper, and returns an `AdminShowcasePreviewResponse` containing
  `preview=True`, `mode`, `config`, and optionally `html`.
- Assertion sketch (not final code): seed draft data and an old published
  snapshot, call preview in mobile mode, assert preview config uses draft values,
  persisted published snapshot remains old, and public GET for the public id
  still returns the old published data or `404`.

**Actions:**

- [ ] Add focused API/core tests for preview mode handling, draft projection,
  explicit preview marker, optional HTML output, owner auth failures, and no
  published-snapshot mutation.
- [ ] Run the narrowest relevant tests and confirm they fail for the expected
  missing endpoint/use case/projection behavior.
- [ ] Make the minimal production changes required for the tests to pass.
- [ ] Re-run the focused tests and confirm they pass.
- [ ] Perform only necessary safe refactoring and re-run the focused tests.
- [ ] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 4: Publish and unpublish immutable snapshots with audit and cache boundary

**Success Criteria:**

- `POST /api/v1/showcases/{id}/publish` validates required public fields from
  the draft, requires at least one enabled offer or a configured fallback, and
  creates a new immutable published snapshot row from draft data.
- Publish copies only approved public data into the snapshot: public settings,
  visible blocks, enabled offers, visible offer fields, URL params/metrics data,
  platform data, preview-compatible widget/showcase data, and custom
  `head`/`body` code as frontend strings.
- Publish increments the publication version, records author user/partner and
  publication time, assigns or reuses a stable opaque `public_id`, switches
  active public visibility atomically, appends a safe audit record, and calls the
  cache invalidation boundary.
- `POST /api/v1/showcases/{id}/unpublish` is protected and owner-scoped,
  increments publication state/version as defined by the implementation
  boundary, removes active public visibility atomically, appends a safe audit
  record, and calls the cache invalidation boundary without deleting immutable
  snapshot history.
- Failed validation, no-auth, foreign-owner, missing-resource, and audit-append
  failure paths leave old public visibility unchanged and do not partially
  publish or unpublish.
- The narrowest relevant checks include
  `rtk uv run pytest -vv -x src/tests/api/test_admin_showcase_publish.py::TestAdminShowcasePublishAPI::test_publish_creates_active_snapshot_and_audit_record`
  and focused storage/core tests for validation and atomic old-or-new visibility.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: `src/api/showcases/endpoints.py`,
  `src/api/showcases/schemas.py`, `src/core/showcases/exceptions.py`,
  `src/core/showcases/schemas.py`, `src/core/showcases/use_cases.py`,
  `src/core/public_config/schemas.py`, `src/api/public_config/schemas.py`,
  `src/core/storages.py`, `src/storages/showcases.py`,
  `src/di/providers/general.py`, `src/di/providers/showcases.py`,
  `src/tests/helpers/api.py`, `src/tests/helpers/factory.py`,
  `src/tests/helpers/storage.py`, `src/tests/api/test_admin_showcase_publish.py`,
  `src/tests/core/showcases/test_publish_admin_showcase_use_case.py`, and
  `src/tests/storages/test_admin_showcase_storage.py`.
- Existing pattern: `src/di/providers/database.py` owns the transaction, so
  publish/unpublish storage and use cases must rely on the request Unit of Work
  for atomic snapshot, visibility, audit, and invalidation-boundary state.
- Code shape sketch (not final code): publish use case owner-checks the
  showcase, builds the public snapshot through the same projection used by
  preview, validates required public fields, calls storage to insert the new
  snapshot and move the active pointer in one transaction, appends audit, then
  invokes a no-op cache invalidator adapter provided by DI.
- Assertion sketch (not final code): seed old published snapshot and draft
  changes, publish, assert public id is stable, version increments, old snapshot
  row remains, active public read sees only the new snapshot, and audit metadata
  excludes raw custom code.

**Actions:**

- [ ] Add focused API/core/storage tests for publish validation, immutable
  snapshot creation, version/author/time metadata, stable public id, audit,
  cache invalidation boundary, and atomic old-or-new visibility.
- [ ] Add focused API/core/storage tests for unpublish behavior, audit,
  cache invalidation boundary, preserved snapshot history, and no partial state
  change on failures.
- [ ] Run the narrowest relevant tests and confirm they fail for the expected
  missing publish/unpublish behavior.
- [ ] Make the minimal production changes required for the tests to pass.
- [ ] Re-run the focused tests and confirm they pass.
- [ ] Perform only necessary safe refactoring and re-run the focused tests.
- [ ] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 5: Expose public published config by public id and explicit resolve binding

**Success Criteria:**

- `GET /api/v1/public/showcases/{public_id}` is public, does not use
  `JwtUserDeps`, returns only the active published snapshot serialized through
  `PublicConfigResponse`, and returns `404` for missing, draft-only,
  unpublished, archived, or inactive snapshot resources.
- `GET /api/v1/public/showcases/resolve?host=...&path=...` is public, does not
  use `JwtUserDeps`, resolves only explicit published route binding rows, and
  returns the same public config payload as public-id lookup.
- Public responses are widgetmarket-compatible JSON and include published
  custom `head`/`body` frontend code only after publication.
- Public responses do not include draft settings, disabled offers, hidden offer
  fields, admin showcase ids, owner/partner/user identifiers, internal database
  ids, audit metadata, custom-code review metadata, service settings, private
  analytics, raw PII, or server-side custom-code metadata.
- Unsupported public methods remain unexposed or return framework-level
  `404`/`405` without private resource data; public reads do not mutate audit,
  analytics, counters, cache, or storage state.
- The narrowest relevant checks include
  `rtk uv run pytest -vv -x src/tests/api/test_public_config_routes.py::TestPublicConfigRoutesAPI::test_get_public_config_returns_active_published_snapshot_only`
  and focused public resolve tests.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: `src/api/public_config/endpoints.py`,
  `src/api/public_config/schemas.py`, `src/core/public_config/schemas.py`,
  `src/core/showcases/exceptions.py`, `src/core/showcases/use_cases.py`,
  `src/core/storages.py`, `src/storages/showcases.py`,
  `src/api/routers.py`, `src/di/providers/showcases.py`,
  `src/tests/helpers/api.py`, `src/tests/helpers/storage.py`,
  `src/tests/api/test_public_config_routes.py`,
  `src/tests/api/test_public_config_schemas.py`, and focused core/storage tests.
- Existing pattern: `src/api/routers.py::root_router` is the only router
  composition point. Public endpoints should be in their own router so public
  auth behavior is easy to review.
- Code shape sketch (not final code): add public read use cases that call
  storage methods such as `get_active_public_snapshot(public_id=...)` and
  `resolve_active_public_snapshot(host=..., path=...)`, then convert the domain
  snapshot through `PublicConfigResponse.from_domain(...)`.
- Assertion sketch (not final code): seed draft data, inactive snapshot history,
  one active snapshot, and an explicit route binding; assert both public GET
  paths return the active snapshot and that serialized JSON does not contain
  draft/admin/private field names.

**Actions:**

- [ ] Add focused API/core/storage tests for public-id lookup, explicit
  host/path resolve lookup, no-auth public access, missing/unpublished/inactive
  `404`, unsupported methods, and no public leakage of draft/private fields.
- [ ] Run the narrowest relevant tests and confirm they fail for the expected
  missing public router/use case/storage behavior.
- [ ] Make the minimal production changes required for the tests to pass.
- [ ] Re-run the focused tests and confirm they pass.
- [ ] Perform only necessary safe refactoring and re-run the focused tests.
- [ ] Run `rtk make quality`, fix all failures, and repeat until successful.
