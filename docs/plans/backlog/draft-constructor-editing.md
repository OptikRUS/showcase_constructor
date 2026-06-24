# Plan: Draft Constructor Editing

## Goal

Implement protected owner-scoped draft editing for showcase settings/text/banner
data, blocks, and offers, backed by PostgreSQL, while keeping public reads on the
published snapshot and leaving unresolved import, publish, and audit details as
explicit product decisions.

## Context

- Current task description resolved from the rendered `ralphex --plan` request:
  implement draft settings/text/banner editing; block management; and offer
  management from `docs/showcase-constructor-tz.md`, with owner-scoped
  PostgreSQL-backed operations and draft-only mutation semantics.
- Root `AGENTS.md`, `/Users/kirillpydev/.codex/RTK.md`,
  `docs/plans/README.md`, `docs/references/examples/ralphex.md`,
  `docs/decisions/mvp-boundaries.md`, `docs/decisions/admin-api-lifecycle.md`,
  `docs/showcase-constructor-tz.md`, and the relevant API/core/storage/DI/test
  references were read before writing this plan.
- `AGENTS.md` references `/Users/optikrus/.codex/RTK.md`, but that file is absent
  in this environment. The available RTK rule requires all shell commands to be
  prefixed with `rtk`.
- No nested `AGENTS.md` files were found under the repository. `README.md` is
  absent, except for `.pytest_cache/README.md`, which is not a project rule file.
- `Makefile` exposes `tests`, `tests-coverage`, `lint`, `types`, `fix`, and
  `quality`; narrow behavior checks should use the project pattern
  `rtk uv run pytest -vv -x ...`.
- Existing live admin auth route pattern:
  `src/api/admin_auth/endpoints.py::get_current_context` uses `JwtUserDeps`,
  creates `src/core/admin_auth/schemas.py::AdminActorContext`, and returns a
  boundary schema.
- `src/api/routers.py::root_router` currently includes only common and admin auth
  routers. Feature routers must be registered there, not in
  `src/api/app.py::create_app`.
- `src/api/exceptions.py` maps admin auth/resource errors centrally. Showcase
  owner/not-found errors already inherit from admin permission/not-found errors.
- `src/core/showcases/schemas.py` currently contains only `AdminShowcase` with
  `id`, `owner_partner_id`, and `title`, plus `AdminShowcaseUpdateParams` with
  only `title`.
- `src/core/showcases/use_cases.py` has owner checks for get/update through
  `AdminShowcaseStorage`, but only the title draft update exists today.
- `src/core/storages.py::AdminShowcaseStorage` has only `get_by_id()` and
  `update_draft()`. No block or offer storage methods exist.
- `src/storages/models.py` contains only SQLAlchemy `Base`; no business tables
  exist. The only migration is `src/migrations/versions/0001_migration_smoke.py`.
- `src/di/providers/database.py` already owns the request-scoped `AsyncSession`
  Unit of Work and commits/rolls back outside storage/use case code.
- `src/tests/fixtures.py::APIFixture`, `FactoryFixture`, and `StorageFixture`,
  `src/tests/helpers/api.py::APIHelper`, `src/tests/helpers/factory.py::FactoryHelper`,
  and `src/tests/helpers/storage.py::StorageHelper` are the shared test surfaces
  to extend.
- `src/api/public_config/schemas.py` and `src/core/public_config/schemas.py`
  already model published public config fields and reject private/public-leak
  fields in tests. Draft APIs must not mutate or expose public snapshots.
- `docs/showcase-constructor-tz.md` defines the requested editable draft fields:
  `designId`, `colorScheme`, widget/offers/text/button colors, `fontFamily`,
  title/subtitle/CTA/meta text, desktop/mobile/mini banners, fallback text,
  block order/visibility/type/title/subtitle/desktop/mobile settings, and offer
  order/enablement/block assignment/CTA/USP/fields/categories/logo/name/site/CPA
  URL/legal data.
- `docs/decisions/mvp-boundaries.md` approves protected owner-scoped admin route
  classes and PostgreSQL durable storage, but still marks exact business table
  design, final audit/outbox details, publication workflow, external offer
  source/import/sync, analytics, billing, custom-domain activation, and event
  schemas as `product decision required`.

## Product/Security Decisions

- Method auth matrix:
  `PATCH /api/v1/showcases/{id} -> token/session auth through current admin JWT context`;
  `GET /api/v1/showcases/{id}/blocks -> token/session auth`;
  `POST /api/v1/showcases/{id}/blocks -> token/session auth`;
  `PATCH /api/v1/showcases/{id}/blocks/{block_id} -> token/session auth`;
  `DELETE /api/v1/showcases/{id}/blocks/{block_id} -> token/session auth`;
  `GET /api/v1/showcases/{id}/offers -> token/session auth`;
  `POST /api/v1/showcases/{id}/offers -> token/session auth`;
  `PATCH /api/v1/showcases/{id}/offers/{offer_id} -> token/session auth`;
  `DELETE /api/v1/showcases/{id}/offers/{offer_id} -> token/session auth`.
- Public read decision: none of the touched admin `GET`, `HEAD`, or `OPTIONS`
  routes are public. This plan must not add app-defined admin `HEAD` or
  `OPTIONS` routes. Public storefront routes continue to read only published
  snapshots.
- Protected methods: every touched admin method requires
  `src.api.auth.deps.JwtUserDeps`, converts to already validated
  `AdminActorContext`, and delegates to exactly one use case.
- Public data: no data returned by the new admin draft endpoints is public data.
  Draft settings, draft blocks, draft offers, hidden offer fields, disabled
  offers, draft fallback text, and draft custom HTML/calculator settings remain
  owner-admin data until a later approved publish flow copies allowed data into a
  published snapshot.
- Identifier exposure: owned admin `showcase_id`, `block_id`, and `offer_id`
  may be returned only to the authenticated owner after the core owner check.
  Internal PostgreSQL primary keys, owner/admin emails, usernames, profile ids,
  tenant/account ids, and foreign-owner data must not be exposed.
- Draft/published separation: `PATCH /api/v1/showcases/{id}` and block/offer
  mutations update draft state only. They must not mutate
  `PublishedPublicConfigSnapshot`, public config schemas, public config routes,
  or any published snapshot column/table.
- Custom HTML/calculator boundary: this plan may store draft block data for
  `custom_html` and `calculator` block types as frontend data only. Backend
  execution, server-side secrets/runtime access, raw end-user PII handling,
  sanitizer policy, and public exposure remain outside this plan unless a later
  focused decision approves them.
- Product decision required: exact durable audit table/outbox fields and
  retention remain unresolved. Before production route behavior is considered
  complete, a focused decision must approve the safe audit metadata for
  settings, block, offer, and custom HTML/calculator draft mutations.
- Product decision required: external offer source/import/sync and CPA-network
  reconciliation remain unresolved. This plan covers persisted manual/admin
  draft offer payloads only.
- Product decision required: publish/unpublish endpoint behavior, cache
  invalidation, snapshot activation, rollback, and public event behavior remain
  unresolved. Disabled offers must be represented in draft with an enabled flag,
  but copying only enabled offers into a live published snapshot belongs to the
  later approved publish flow.

## Implementation Notes

- Existing API pattern: `src/api/admin_auth/endpoints.py` uses `DishkaRoute`,
  `JwtUserDeps`, and a boundary response schema. New showcase endpoints should
  follow that shape under `src/api/showcases/`.
- Existing router composition: register the new router only in
  `src/api/routers.py::root_router`.
- Existing core pattern: `src/core/showcases/use_cases.py` performs owner checks
  by reading `AdminShowcaseStorage.get_by_id()` before mutation. Reuse that
  pattern for settings, blocks, and offers.
- Existing storage rule: concrete SQLAlchemy storage belongs under
  `src/storages/`, returns domain schemas, and never calls `session.commit()` or
  `session.begin()`.
- Expected endpoint sketch:
  ```python
  # sketch only; inspect real files before implementation
  @router.patch(path="/{showcase_id}", status_code=status.HTTP_200_OK)
  async def patch_showcase_draft(
      showcase_id: str,
      body: AdminShowcaseDraftPatchRequest,
      user: JwtUserDeps,
      use_case: FromDishka[UpdateAdminShowcaseDraftUseCase],
  ) -> AdminShowcaseDraftResponse:
      context = AdminActorContext(user_id=user.user_id, partner_id=user.partner_id)
      result = await use_case.execute(
          showcase_id=showcase_id,
          params=body.to_domain(),
          context=context,
      )
      return AdminShowcaseDraftResponse.from_domain(showcase=result)
  ```
- Expected storage sketch:
  ```python
  # sketch only; inspect real files before implementation
  class DatabaseAdminShowcaseStorage(AdminShowcaseStorage):
      async def update_draft_settings(
          self,
          *,
          showcase_id: str,
          params: AdminShowcaseDraftSettingsPatchParams,
      ) -> AdminShowcaseDraft:
          model = await self.session.scalar(
              update(AdminShowcaseModel)
              .where(AdminShowcaseModel.id == showcase_id)
              .values(draft_settings=params.to_storage_dict())
              .returning(AdminShowcaseModel)
          )
          if model is None:
              raise AdminShowcaseNotFoundError
          return model.to_draft_domain()
  ```
- Expected test assertion sketch:
  ```python
  response = self.api.patch_admin_showcase_draft(
      showcase_id="showcase-1",
      json={"settings": {"designId": "modern", "textTitle": "New title"}},
  )
  assert response.status_code == codes.OK
  assert response.json()["settings"]["designId"] == "modern"
  ```
- Edge cases:
  - unauthenticated admin draft routes use `self.no_auth_api` in separate
    `Test*NoAuthAPI` classes;
  - foreign-owned resources return `403`; missing resources return `404`;
  - failed `401`, `403`, and `404` paths do not mutate draft or published state;
  - missing fields mean no change, explicit `null` clears nullable draft fields
    only where the schema permits it;
  - block order and offer manual position updates must be persisted and returned
    consistently after database-side updates;
  - hidden offer fields and disabled offers remain visible to the owner-admin
    draft API but are excluded from future published snapshot projection;
  - `custom_html` and `calculator` block settings are stored as data only and
    never executed on the backend;
  - no new dependency is required for PostgreSQL JSON/JSONB storage because
    SQLAlchemy and asyncpg are already present.

## Constraints

- Follow `AGENTS.md` and applicable nested instructions.
- Use existing project patterns.
- Use `rtk` for shell commands.
- Do not change architecture without necessity.
- Do not add new dependencies unless the plan explicitly updates
  `pyproject.toml` and `uv.lock`; this plan should not need new dependencies.
- Do not create runtime config beyond the existing database settings unless a
  later task proves it is required.
- Do not create standalone `src/tests/config/`, `src/tests/di/`, or
  `src/tests/migrations/` directories for infrastructure mechanics.
- Do not expose draft data through public config APIs.
- Do not implement publish/unpublish, external offer import/sync, analytics,
  billing, custom-domain behavior, or backend execution of custom HTML/code in
  this plan.
- Apply TDD to behavior changes.
- Each Task should be small enough to finish with green validation.

## Validation Commands

- `rtk make lint`
- `rtk make types`
- `rtk make tests`
- `rtk make quality`

## Tasks

### Task 1: Record the focused draft editing boundary

**Success Criteria:**

- A focused decision record under `docs/decisions/` approves the minimal schema,
  owner-admin response fields, and draft-only mutation boundary for settings,
  blocks, and offers.
- The record keeps final audit/outbox shape, external offer source/import/sync,
  and publish/unpublish snapshot activation as `product decision required`.
- The record states that `custom_html` and `calculator` draft block data is
  stored as frontend data only and is never executed by the backend.
- No application code, migration, route, storage, dependency, or public schema is
  changed in this Task.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely file: create `docs/decisions/draft-constructor-editing.md`.
- Existing pattern: `docs/decisions/admin-api-lifecycle.md` and
  `docs/decisions/mvp-boundaries.md` use boundary tables plus explicit
  `product decision required` rows.
- Decision shape sketch: approve protected owner-scoped admin draft editing for
  the requested fields, approve owner-only admin exposure of draft `block_id` and
  `offer_id`, and leave publication/audit/import behavior unresolved.
- Validation sketch: `rtk rg -n "draft editing|block_id|offer_id|product decision required" docs/decisions/draft-constructor-editing.md`.

**Actions:**

- [x] Add the focused decision record for draft settings, block, and offer editing.
- [x] Verify it preserves unresolved audit, import/sync, and publish behavior as `product decision required`.
- [x] Confirm no application, migration, dependency, or public schema file changed in this Task.
- [x] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 2: Add PostgreSQL draft storage schema

**Success Criteria:**

- A new Alembic migration creates the approved PostgreSQL tables/columns for
  owner-scoped showcases, draft settings, draft blocks, draft offers, and
  separate published snapshot storage or a nullable published snapshot column.
- Internal PostgreSQL primary keys remain private; route/admin ids are stored as
  explicit string identifiers.
- SQLAlchemy models in `src/storages/models.py` convert ORM rows to the new
  domain draft schemas without returning ORM objects from storage.
- `src/tests/storages/test_database_migrations.py::TestDatabaseMigrations` is
  updated to the new head revision.
- The focused migration command
  `rtk uv run pytest -vv -x src/tests/storages/test_database_migrations.py::TestDatabaseMigrations::test_upgrades_to_head_revision`
  passes.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: `src/migrations/versions/0002_create_draft_constructor_tables.py`,
  `src/storages/models.py`, `src/tests/storages/test_database_migrations.py`.
- Existing pattern: `src/migrations/versions/0001_migration_smoke.py` names
  revisions without dates; `docs/references/examples/storages.md` shows
  SQLAlchemy model-to-domain conversion.
- Code shape sketch: use PostgreSQL JSON/JSONB-compatible SQLAlchemy columns for
  draft settings and flexible block/offer payloads, plus sortable integer fields
  for block order and offer manual position when the decision record approves
  that shape.
- Assertion sketch: migration smoke reads `alembic_version` through
  `StorageHelper.get_current_alembic_version()` and expects the new revision id.

**Actions:**

- [x] Add or update one focused migration smoke test for the new head revision.
- [x] Run the focused migration smoke test and confirm it fails for the missing revision.
- [x] Add the minimal migration and SQLAlchemy model changes for draft constructor storage.
- [x] Re-run the focused migration smoke test and confirm it passes.
- [x] Perform only necessary safe refactoring and re-run the focused migration smoke test.
- [x] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 3: Implement database storage primitives for draft settings

**Success Criteria:**

- `AdminShowcaseStorage` exposes draft settings read/update methods required by
  the settings PATCH use case.
- Concrete PostgreSQL storage updates only draft settings/text/banner fields and
  leaves any published snapshot storage unchanged.
- Storage tests prove same-row draft update, explicit nullable clearing where
  allowed, not-found behavior, and published snapshot preservation.
- The focused command
  `rtk uv run pytest -vv -x src/tests/storages/test_admin_showcase_storage.py::TestDatabaseAdminShowcaseStorage::test_updates_draft_settings_without_changing_published_snapshot`
  passes.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: `src/core/storages.py`, `src/core/showcases/schemas.py`,
  `src/storages/showcases.py`, `src/tests/storages/test_admin_showcase_storage.py`,
  `src/tests/helpers/factory.py`, `src/tests/helpers/storage.py`.
- Existing pattern: `src/core/storages.py::AdminShowcaseStorage` owns storage
  interface methods; storage helpers live in `src/tests/helpers/storage.py`.
- Code shape sketch: add domain dataclasses such as
  `AdminShowcaseDraftSettings`, `AdminShowcaseDraftPatchParams`, and an
  `AdminShowcaseDraft` aggregate only for verified fields from the task/spec.
- Assertion sketch: insert a showcase with draft and published payloads, update
  `design_id`, `text_title`, and `image_banner_mobile`, then read back both
  draft and published data and assert only draft changed.

**Actions:**

- [x] Add focused storage tests for draft settings update and published snapshot preservation.
- [x] Run the focused storage test and confirm it fails for the missing storage behavior.
- [x] Extend the core storage interface, domain schemas, concrete storage, and storage helper minimally.
- [x] Re-run the focused storage test and confirm it passes.
- [x] Perform only necessary safe refactoring and re-run the focused storage test.
- [x] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 4: Expose protected draft settings PATCH

**Success Criteria:**

- `PATCH /api/v1/showcases/{id}` accepts draft settings/text/banner fields from
  the task description using project boundary schema aliases.
- The endpoint requires current admin auth, builds `AdminActorContext` only from
  `JwtUserDeps`, delegates to one use case, and returns owner draft data.
- Same-owner requests update draft only; no-auth returns `401`; foreign owner
  returns `403`; missing showcase returns `404`.
- API tests use `APIFixture.api` for authenticated cases and a separate
  `TestAdminShowcaseDraftSettingsNoAuthAPI` class with `self.no_auth_api`.
- The focused command
  `rtk uv run pytest -vv -x src/tests/api/test_admin_showcase_draft_settings.py::TestAdminShowcaseDraftSettingsAPI::test_patches_draft_settings_only`
  passes.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: `src/api/showcases/endpoints.py`, `src/api/showcases/schemas.py`,
  `src/api/showcases/__init__.py`, `src/api/routers.py`,
  `src/core/showcases/use_cases.py`, `src/di/providers/showcases.py`,
  `src/di/container.py`, `src/tests/api/test_admin_showcase_draft_settings.py`,
  `src/tests/helpers/api.py`.
- Existing pattern: `src/api/admin_auth/endpoints.py` for auth dependency and
  `src/api/routers.py::root_router.include_router(...)` for registration.
- Code shape sketch: `AdminShowcaseDraftPatchRequest.to_domain()` creates patch
  params with only provided fields; `UpdateAdminShowcaseDraftUseCase` performs
  the owner check before calling the storage update method.
- Assertion sketch: response JSON includes camelCase fields such as `designId`,
  `colorScheme`, `fontFamily`, `textTitle`, `textSubtitle`, `textButton`,
  `metaTitle`, `metaDescription`, `imageBannerDesktop`,
  `imageBannerMobile`, `imageBannerMini`, and `fallbackText`.

**Actions:**

- [x] Add focused API tests for same-owner draft settings patch, no-auth, foreign-owner, missing showcase, and published snapshot preservation.
- [x] Run the focused API test and confirm it fails for the missing route/use case.
- [x] Add the minimal endpoint, boundary schemas, use case, provider wiring, router registration, and API helper method.
- [x] Re-run the focused API test and confirm it passes.
- [x] Perform only necessary safe refactoring and re-run the focused API test.
- [x] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 5: Implement block list and create

**Success Criteria:**

- `GET /api/v1/showcases/{id}/blocks` returns only the authenticated owner's
  draft blocks ordered by draft order.
- `POST /api/v1/showcases/{id}/blocks` creates one draft block with supported
  type, order, visibility, title, subtitle, and desktop/mobile settings.
- Supported block types are exactly `hero`, `offers`, `banner`, `banner_card`,
  `advantages`, `legal_footer`, `popup_offers`, `custom_html`, and `calculator`.
- Same-owner behavior is persisted in PostgreSQL; no-auth returns `401`;
  foreign owner returns `403`; missing showcase returns `404`.
- The focused command
  `rtk uv run pytest -vv -x src/tests/api/test_admin_showcase_blocks.py::TestAdminShowcaseBlocksAPI::test_creates_and_lists_draft_blocks`
  passes.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: `src/core/showcases/schemas.py`,
  `src/core/showcases/use_cases.py`, `src/core/storages.py`,
  `src/storages/showcases.py`, `src/api/showcases/endpoints.py`,
  `src/api/showcases/schemas.py`, `src/tests/api/test_admin_showcase_blocks.py`,
  `src/tests/storages/test_admin_showcase_storage.py`,
  `src/tests/helpers/api.py`, `src/tests/helpers/factory.py`,
  `src/tests/helpers/storage.py`.
- Existing pattern: owner check in `UpdateAdminShowcaseUseCase` happens before
  mutation. Use one use case per endpoint.
- Code shape sketch: add `ListAdminShowcaseBlocksUseCase` and
  `CreateAdminShowcaseBlockUseCase`; storage list/create methods operate on
  draft block rows and return domain block schemas.
- Assertion sketch: create two blocks with different order values, list them,
  and assert returned `id`, `type`, `order`, `visible`, `title`, `subtitle`,
  `desktopSettings`, and `mobileSettings` order matches persisted draft order.

**Actions:**

- [x] Add focused API/core/storage tests for list and create block behavior.
- [x] Run the focused block list/create test and confirm it fails for the missing behavior.
- [x] Add minimal domain schemas, use cases, storage methods, endpoint methods, boundary schemas, DI wiring, and helpers.
- [x] Re-run the focused block list/create test and confirm it passes.
- [x] Perform only necessary safe refactoring and re-run the focused block test.
- [x] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 6: Implement block patch and delete

**Success Criteria:**

- `PATCH /api/v1/showcases/{id}/blocks/{block_id}` updates only the addressed
  owned draft block's mutable fields.
- `DELETE /api/v1/showcases/{id}/blocks/{block_id}` removes only the addressed
  owned draft block and leaves other blocks, offers, and any published snapshot
  unchanged.
- Patch supports order, visibility, title, subtitle, type-specific settings, and
  desktop/mobile settings without backend execution of `custom_html` or
  `calculator` content.
- No-auth returns `401`; foreign owner returns `403`; missing showcase or block
  returns `404`.
- The focused command
  `rtk uv run pytest -vv -x src/tests/api/test_admin_showcase_blocks.py::TestAdminShowcaseBlocksAPI::test_patches_and_deletes_draft_block`
  passes.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: same block files from Task 5.
- Existing pattern: `src/core/showcases/exceptions.py` already maps showcase
  not-found/permission errors through centralized API handlers; add block
  not-found errors in the same domain exception style.
- Code shape sketch: add `PatchAdminShowcaseBlockUseCase` and
  `DeleteAdminShowcaseBlockUseCase`; each first verifies the showcase owner,
  then calls a storage method scoped by both `showcase_id` and `block_id`.
- Assertion sketch: patch one block's `order` and `visible`, delete a different
  block, then list blocks and assert only the targeted draft rows changed.

**Actions:**

- [x] Add focused API/core/storage tests for block patch, delete, owner checks, not-found, and published snapshot preservation.
- [x] Run the focused block patch/delete test and confirm it fails for the missing behavior.
- [x] Add minimal domain params, use cases, storage methods, endpoint methods, boundary schemas, and helpers.
- [x] Re-run the focused block patch/delete test and confirm it passes.
- [x] Perform only necessary safe refactoring and re-run the focused block test.
- [x] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 7: Implement offer list and create

**Success Criteria:**

- `GET /api/v1/showcases/{id}/offers` returns only the authenticated owner's
  draft offers ordered by manual order and block assignment.
- `POST /api/v1/showcases/{id}/offers` creates one draft offer with enablement,
  manual order, block assignment, CTA/USP overrides, visible fields, categories,
  logos, display names, CPA URL, legal entity, INN, and optional `erid`.
- Draft offer fields use `{key, value, visible}` and preserve hidden fields for
  owner-admin editing.
- Same-owner behavior is persisted in PostgreSQL; no-auth returns `401`;
  foreign owner returns `403`; missing showcase or block assignment returns `404`
  or a domain validation error mapped consistently through `src/api/exceptions.py`.
- The focused command
  `rtk uv run pytest -vv -x src/tests/api/test_admin_showcase_offers.py::TestAdminShowcaseOffersAPI::test_creates_and_lists_draft_offers`
  passes.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: `src/core/showcases/schemas.py`,
  `src/core/showcases/use_cases.py`, `src/core/showcases/exceptions.py`,
  `src/core/storages.py`, `src/storages/showcases.py`,
  `src/api/showcases/endpoints.py`, `src/api/showcases/schemas.py`,
  `src/api/exceptions.py`, `src/tests/api/test_admin_showcase_offers.py`,
  `src/tests/storages/test_admin_showcase_storage.py`,
  `src/tests/helpers/api.py`, `src/tests/helpers/factory.py`,
  `src/tests/helpers/storage.py`.
- Existing pattern: public offer response fields in
  `src/api/public_config/schemas.py::PublicOfferResponse` show camelCase aliases
  for `offerCategories`, `logoUrl`, `roundedLogoUrl`, `siteName`, and `url`.
  Admin draft schemas may include extra owner-only fields such as `enabled`,
  `manualOrder`, `blockId`, `ctaText`, `uspText`, `legalEntity`, `inn`, and
  `erid`.
- Code shape sketch: add `ListAdminShowcaseOffersUseCase` and
  `CreateAdminShowcaseOfferUseCase`; storage creates draft offer rows scoped by
  `showcase_id`.
- Assertion sketch: create enabled and disabled offers with fields, then list and
  assert both are visible to owner-admin draft API with field visibility flags
  preserved.

**Actions:**

- [ ] Add focused API/core/storage tests for offer list and create behavior.
- [ ] Run the focused offer list/create test and confirm it fails for the missing behavior.
- [ ] Add minimal domain schemas, exceptions, use cases, storage methods, endpoint methods, boundary schemas, exception mapping, and helpers.
- [ ] Re-run the focused offer list/create test and confirm it passes.
- [ ] Perform only necessary safe refactoring and re-run the focused offer test.
- [ ] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 8: Implement offer patch and delete

**Success Criteria:**

- `PATCH /api/v1/showcases/{id}/offers/{offer_id}` updates only the addressed
  owned draft offer's mutable fields, including enable/disable, manual order,
  block assignment, CTA/USP overrides, fields, categories, logo URLs, display
  names, CPA URL, legal entity, INN, and `erid`.
- `DELETE /api/v1/showcases/{id}/offers/{offer_id}` removes only the addressed
  owned draft offer and leaves other offers, blocks, and any published snapshot
  unchanged.
- Disabled offers remain in the owner-admin draft API and are marked
  `enabled: false` for later publish filtering.
- No-auth returns `401`; foreign owner returns `403`; missing showcase, offer, or
  block assignment returns the approved error status.
- The focused command
  `rtk uv run pytest -vv -x src/tests/api/test_admin_showcase_offers.py::TestAdminShowcaseOffersAPI::test_patches_and_deletes_draft_offer`
  passes.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: same offer files from Task 7.
- Existing pattern: storage methods perform persistence operations only; block
  assignment and owner checks remain use case responsibilities after loading the
  owned showcase.
- Code shape sketch: add `PatchAdminShowcaseOfferUseCase` and
  `DeleteAdminShowcaseOfferUseCase`; storage methods are scoped by both
  `showcase_id` and `offer_id`.
- Assertion sketch: patch an offer to `enabled: false`, change `manualOrder` and
  a hidden field, delete another offer, list offers, and assert only targeted
  draft rows changed while published snapshot readback is unchanged.

**Actions:**

- [ ] Add focused API/core/storage tests for offer patch, delete, enable/disable, owner checks, not-found, and published snapshot preservation.
- [ ] Run the focused offer patch/delete test and confirm it fails for the missing behavior.
- [ ] Add minimal domain params, use cases, storage methods, endpoint methods, boundary schemas, and helpers.
- [ ] Re-run the focused offer patch/delete test and confirm it passes.
- [ ] Perform only necessary safe refactoring and re-run the focused offer test.
- [ ] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 9: Guard public snapshot separation and disabled-offer projection

**Success Criteria:**

- Tests prove draft settings, draft blocks, draft offers, disabled offers, and
  hidden offer fields do not appear in existing public config responses unless a
  later approved publish flow explicitly copies allowed data into a published
  snapshot.
- A pure domain projection helper, if added by the approved decision record,
  excludes disabled offers and hidden fields from a candidate published snapshot
  without registering publish/unpublish routes or mutating live public state.
- Existing `src/tests/api/test_public_config_schemas.py` private-field leak tests
  remain green.
- The focused command
  `rtk uv run pytest -vv -x src/tests/api/test_public_config_schemas.py::TestPublicConfigResponseSchema::test_excludes_draft_and_private_fields`
  passes.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: `src/core/public_config/schemas.py`,
  `src/api/public_config/schemas.py`, `src/tests/api/test_public_config_schemas.py`,
  `src/tests/core/public_config/test_public_config_schemas.py`,
  `src/tests/helpers/factory.py`.
- Existing pattern: public config response schemas use `extra="forbid"` and
  already reject private fields in nested offers.
- Code shape sketch: keep public config schema unchanged unless the decision
  record approves a small pure projection helper; do not add route handlers,
  cache invalidation, event writes, publish actions, or public identifiers.
- Assertion sketch: serialize a published snapshot while draft storage contains
  disabled and hidden draft offers, then assert public JSON contains only the
  existing published snapshot offer data.

**Actions:**

- [ ] Add focused public config separation tests for draft-only data, disabled offers, and hidden fields.
- [ ] Run the focused public config test and confirm it fails only if public schemas leak draft/private data.
- [ ] Add the minimal schema/projection adjustment needed by the approved decision record, or classify the Task as `coverage-only` if existing schemas already pass.
- [ ] Re-run the focused public config test and confirm it passes.
- [ ] Perform only necessary safe refactoring and re-run the focused public config test.
- [ ] Run `rtk make quality`, fix all failures, and repeat until successful.
