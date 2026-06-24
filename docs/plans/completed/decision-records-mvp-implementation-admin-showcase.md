# Plan: Decision Records MVP Implementation Boundary

## Goal

Update the decision records so MVP implementation planning can proceed for admin
showcase routes, storage, public identifiers, published snapshot exposure, audit
events, domain verification, and custom-code permissions without implementing
business code.

## Context

- Current task description resolved from the rendered `ralphex --plan` request:
  `Актуализируй decision records так, чтобы разблокировать MVP-implementation для: admin showcase routes, in-memory MVP storage или выбранный persistence boundary, public identifier model, published snapshot exposure, audit/event durability level, domain verification MVP method и custom code MVP permissions. Не реализуй бизнес-код. Результат должен явно переводить выбранные пункты из product decision required в approved MVP boundary либо оставлять их заблокированными с причиной.`
- Root `AGENTS.md`, `/Users/kirillpydev/.codex/RTK.md`,
  `docs/plans/README.md`, `docs/references/examples/ralphex.md`,
  `docs/decisions/mvp-boundaries.md`, and
  `docs/decisions/admin-api-lifecycle.md` were read before writing this plan.
- `AGENTS.md` references `/Users/optikrus/.codex/RTK.md`, but that file is
  absent in this environment. The available RTK rule requires all shell commands
  to be prefixed with `rtk`.
- No nested `AGENTS.md` files were found under the repository.
- `README.md` is absent; project rules come from `AGENTS.md`, `pyproject.toml`,
  `Makefile`, `docs/plans/README.md`, and `docs/references/examples/`.
- `Makefile` exposes `tests`, `tests-coverage`, `lint`, `types`, `fix`, and
  `quality`; validation commands for this plan use only the required
  `rtk make ...` commands below.
- `src/api/app.py::create_app` includes only
  `src/api/routers.py::root_router` and disables docs, OpenAPI, and ReDoc.
- `src/api/routers.py::root_router` currently includes
  `src/api/common/endpoints.py::router` and
  `src/api/admin_auth/endpoints.py::router`.
- `GET /health` is the only confirmed public runtime route.
- `GET /api/v1/admin/auth/context` is protected by the existing JWT bearer
  adapter in `src/api/auth/deps.py`; `src/api/auth/schemas.py::JwtUser`
  validates nonblank `user_id` and `partner_id` from token subject data.
- `src/config/settings.py` already contains auth settings. There is no concrete
  persistence settings class, no `src/storages/`, and no migrations directory.
- `src/core/storages.py::AdminShowcaseStorage` already defines an admin showcase
  storage interface with `get_by_id()` and `update_draft()`, but no concrete
  storage implementation exists.
- `src/core/showcases/use_cases.py` already contains `GetAdminShowcaseUseCase`
  and `UpdateAdminShowcaseUseCase`; current tests cover same-partner access,
  foreign-partner denial, and not-found propagation.
- `src/tests/api/test_admin_showcase_lifecycle_routes.py` currently verifies
  candidate admin lifecycle routes remain unregistered without approved
  decisions.
- `src/core/public_config/schemas.py` and `src/api/public_config/schemas.py`
  already define published public config snapshot and response schemas, while
  `src/tests/api/test_public_config_routes.py` verifies the public config route
  is still not registered.
- Current decision records keep admin lifecycle route permissions, public
  identifiers, public storefront route exposure, persistence backend, domain
  verification, audit/event durability, and custom-code permissions as
  `product decision required`.
- This plan is documentation-only. It must not add business code, FastAPI
  routes, DI providers, concrete storage, dependencies, runtime config,
  migrations, or tests unless the plan is amended.

## Product/Security Decisions

- Method auth matrix: `GET /health -> public`; `GET /api/v1/admin/auth/context`
  -> protected by the MVP JWT bearer adapter; future admin showcase
  `POST`, `GET`, `PATCH`, clone/archive/restore methods must be recorded in
  decision records as either protected by current admin context or still
  blocked with a reason.
- Public read decision: no admin showcase route is public. Public storefront
  `GET`/`HEAD`/`OPTIONS` routes remain unimplemented by this plan; decision
  records must explicitly approve or block future public published-snapshot
  reads.
- Protected methods: future admin showcase create, list own, get own, patch
  draft, clone, archive, and any restore/unarchive operation require an approved
  authenticated admin/partner boundary before route registration.
- Public data: only published snapshot fields explicitly approved in the
  decision records may be exposed publicly. Draft data, private service
  settings, owner/admin identifiers, tenant/account identifiers, and internal
  storage identifiers remain forbidden unless explicitly approved with a
  rationale.
- Identifier exposure: public identifiers must be either approved as an opaque
  public identifier model or left blocked. Internal database ids, admin emails,
  usernames, profile identifiers, and partner/tenant/account identifiers must
  not be exposed publicly by default.
- Product decision required: if a listed area cannot be resolved from this task
  request, existing contracts, or an explicit product/security decision, the
  decision record must leave that area blocked with a concrete reason instead
  of inventing an implementation choice.

## Constraints

- Follow `AGENTS.md` and applicable project references.
- Save new plans under `docs/plans/backlog/`.
- Do not create or use `docs/plans/backlog/completed/`.
- Do not create files under `docs/superpowers/plans/`.
- Do not implement business code, FastAPI routes, DI providers, concrete
  storages, settings, migrations, or dependencies in this decision-record task.
- Keep decision records consistent with existing code: JWT subject validation
  stays in `src/api/auth/*`, core context dataclasses remain already-validated
  domain inputs, and `src/api/routers.py::root_router` remains the only router
  composition point for future route work.
- Do not add new dependencies unless a later implementation plan explicitly
  updates both `pyproject.toml` and `uv.lock`.
- Documentation-only tasks do not need artificial RED/GREEN tests.
- Each Task should be small enough to finish with green validation.

## Validation Commands

- `rtk rg --files .ralphex docs/plans docs/references/examples`
- `rtk rg -n "^### Task|^- \\[ \\]" docs/plans .ralphex/prompts`
- `rtk ralphex --config-dir=.ralphex --version`
- `rtk make lint`
- `rtk make types`
- `rtk make tests`
- `rtk make quality`

## Tasks

### Task 1: Decide admin showcase route MVP boundary

**Success Criteria:**

- `docs/decisions/admin-api-lifecycle.md` records each candidate admin showcase
  method and path as either an approved MVP boundary or blocked with a concrete
  reason.
- The record explicitly covers create, list own, get own, patch draft, clone,
  archive, and restore/unarchive.
- The record states that no admin showcase route is public.
- The record states whether `HEAD` and `OPTIONS` are intentionally not
  app-defined in the MVP, protected by the same auth boundary, or still blocked.
- The record defines the authenticated admin response-field boundary for ids,
  owner/partner fields, public ids or slugs, title, status, snapshot metadata,
  timestamps, archive metadata, and restore metadata, or keeps specific fields
  blocked with a reason.
- `docs/decisions/mvp-boundaries.md` references the focused route decision
  without contradicting it.
- No source code, runtime config, dependency, concrete storage, or migration
  file is changed.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: `docs/decisions/admin-api-lifecycle.md` and
  `docs/decisions/mvp-boundaries.md`.
- Existing pattern: `docs/decisions/admin-api-lifecycle.md` already lists the
  requested lifecycle surface and required product/security decisions.
- Decision shape sketch: replace each resolved `product decision required` row
  with `Approved MVP boundary` plus rationale, and leave unresolved rows as
  `product decision required` with a concrete blocking reason.
- Assertion sketch: search the two decision records for the exact route methods,
  `Approved MVP boundary`, and any remaining `product decision required` reason.

**Actions:**

- [x] Update `docs/decisions/admin-api-lifecycle.md` with the admin showcase
  method auth matrix and route-specific approval/blocking status.
- [x] Update `docs/decisions/mvp-boundaries.md` so the Admin API section points
  to the same admin showcase route boundary.
- [x] Verify the decision records do not approve public admin access or
  ambiguous identifier exposure.
- [x] Confirm the diff contains only intended decision-record documentation
  changes.
- [x] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 2: Decide MVP storage and persistence boundary

**Success Criteria:**

- `docs/decisions/mvp-boundaries.md` states the MVP storage choice as either
  in-memory MVP storage or a selected persistence boundary, or leaves storage
  blocked with a concrete reason.
- If in-memory MVP storage is approved, the record states that it is process
  local, non-durable, test/demo scoped, and not a substitute for production
  persistence.
- If durable persistence is approved instead, the record names the backend,
  migration boundary, runtime config boundary, ownership model, and transaction
  boundary.
- The record stays aligned with project rules: concrete implementations belong
  under `src/storages/`, storage interfaces are core-owned, and DI providers own
  the Unit of Work.
- The record acknowledges the current `src/core/storages.py::AdminShowcaseStorage`
  interface and the absence of concrete `src/storages/` implementations.
- No source code, runtime config, dependency, concrete storage, or migration
  file is changed.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely file: `docs/decisions/mvp-boundaries.md`.
- Existing pattern: the current `## Persistence` section uses a table for
  backend choice, runtime config, storage layer, core storage interfaces,
  migrations, transaction boundary, and storage behavior.
- Decision shape sketch: change only the rows whose decision is now explicit;
  leave unresolved durable-production questions blocked instead of silently
  approving database work.
- Assertion sketch: verify the Persistence section contains the selected storage
  boundary and does not mention `repositories` or `repos` as approved layers.

**Actions:**

- [x] Update the Persistence section with the selected MVP storage boundary or
  an explicit blocked reason.
- [x] State whether future implementation may add `src/storages/`,
  persistence-specific `src/config`, and migrations.
- [x] Preserve the DI-owned transaction boundary and `storages` naming rule.
- [x] Confirm the diff contains only intended decision-record documentation
  changes.
- [x] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 3: Decide public identifier model

**Success Criteria:**

- `docs/decisions/mvp-boundaries.md` records the public identifier model as an
  approved MVP boundary or leaves it blocked with a concrete reason.
- The record states whether future public reads use an opaque public showcase id,
  public slug, custom domain, domain plus path, another scheme, or no public
  identifier in MVP.
- The record explicitly forbids public exposure of internal database ids,
  owner/admin identifiers, tenant/account identifiers, emails, usernames, and
  profile identifiers unless a specific field is approved with a rationale.
- The decision is consistent with existing public config schemas, where
  published snapshots have an `id` but the live public route is not registered.
- No source code, runtime config, dependency, concrete storage, or migration
  file is changed.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely file: `docs/decisions/mvp-boundaries.md`.
- Existing pattern: the current `## Public Data And Identifiers` section lists
  field classes, public exposure status, and rationale.
- Decision shape sketch: add a clear identifier row such as opaque public id,
  slug, custom domain, or blocked reason; keep internal/private identifiers
  explicitly forbidden.
- Assertion sketch: verify the public identifier row no longer says only
  `product decision required` unless the task intentionally keeps it blocked
  with a reason.

**Actions:**

- [x] Update the public identifier rows with the approved identifier model or a
  concrete blocked reason.
- [x] Record why the identifier does not expose internal storage or owner
  identity.
- [x] Align any public-route wording with the identifier decision without
  registering a route.
- [x] Confirm the diff contains only intended decision-record documentation
  changes.
- [x] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 4: Decide published snapshot exposure boundary

**Success Criteria:**

- `docs/decisions/mvp-boundaries.md` states which published snapshot fields may
  be exposed publicly, or leaves specific field groups blocked with reasons.
- The record distinguishes published snapshot data from draft data and admin-only
  data.
- The record explicitly covers `id`, `affiliateId`, `type`, `settings`,
  `platform.id`, `blocks`, `widgetInfo`, URL params tools, `metricsTool`,
  `offers`, `triggerGroups`, and
  `is_need_to_send_offers_display_and_positions`, using the existing public
  config contract as the verified candidate shape.
- The record continues to forbid draft version ids, private stats, service
  settings, owner/admin identifiers, tenant/account identifiers, and internal
  offer/block ids.
- The record states that approving the exposure boundary does not register a
  public route by itself.
- No source code, runtime config, dependency, concrete storage, or migration
  file is changed.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely file: `docs/decisions/mvp-boundaries.md`.
- Existing pattern: `src/api/public_config/schemas.py::PublicConfigResponse`
  and `src/tests/api/test_public_config_schemas.py` show the current candidate
  published snapshot response shape.
- Decision shape sketch: add a published-snapshot exposure table with allowed
  field groups and forbidden field groups.
- Assertion sketch: verify the decision record names both allowed public fields
  and forbidden private/draft fields.

**Actions:**

- [x] Update the Public Data And Identifiers section with the published snapshot
  exposure boundary.
- [x] Mark each field group as approved public data or blocked with a concrete
  reason.
- [x] State that route exposure remains a separate implementation decision unless
  the public route method is explicitly approved in the same record.
- [x] Confirm the diff contains only intended decision-record documentation
  changes.
- [x] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 5: Decide audit and event durability level

**Success Criteria:**

- `docs/decisions/mvp-boundaries.md` records the MVP audit/event durability
  level as an approved boundary or leaves it blocked with a concrete reason.
- The record explicitly covers admin create, patch, clone, archive,
  restore/unarchive, publishing changes, domain verification changes, and
  custom-code permission/content changes.
- If best-effort logging, in-memory audit records, durable database records,
  outbox events, external event streams, or another mechanism is approved, the
  record states the retention and implementation boundary clearly enough for a
  future implementation plan.
- The record states whether the durability choice depends on the storage
  boundary from Task 2.
- No source code, runtime config, dependency, concrete storage, or migration
  file is changed.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely file: `docs/decisions/mvp-boundaries.md`.
- Existing pattern: the current `## Audit And Events` section lists audited
  action classes and marks their durability as `product decision required`.
- Decision shape sketch: update each audited action class to approved boundary
  or blocked reason; avoid implying that unaudited mutations are acceptable by
  default.
- Assertion sketch: verify the Audit And Events section names the durability
  mechanism and the feature plans it unblocks or still blocks.

**Actions:**

- [x] Update the Audit And Events section with the approved durability level or
  concrete blocked reason.
- [x] State how the durability level applies to admin showcase mutations,
  publishing, domain verification, and custom-code changes.
- [x] Cross-check the durability wording against the storage boundary from
  Task 2.
- [x] Confirm the diff contains only intended decision-record documentation
  changes.
- [x] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 6: Decide domain verification MVP method

**Success Criteria:**

- `docs/decisions/mvp-boundaries.md` records the MVP domain verification method
  as an approved boundary or leaves it blocked with a concrete reason.
- The record states whether MVP uses DNS TXT, CNAME, HTTP file validation,
  email/manual verification, no custom domains, or another explicit method.
- The record covers token format and storage, retry behavior, expiration,
  failure handling, activation after verification, and public/admin visibility
  of verification status, or keeps specific questions blocked with reasons.
- If custom domains are out of MVP, the record states that as an approved
  boundary instead of leaving the implementation to infer behavior.
- No source code, runtime config, dependency, concrete storage, or migration
  file is changed.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely file: `docs/decisions/mvp-boundaries.md`.
- Existing pattern: the current `## Domain Verification` section lists each
  verification question and the feature plan it blocks.
- Decision shape sketch: update the ownership proof method and dependent rows,
  leaving unresolved retry/storage/public-visibility details blocked if they are
  not part of the MVP decision.
- Assertion sketch: verify the Domain Verification section clearly says either
  which method is approved or why verification remains blocked.

**Actions:**

- [x] Update the Domain Verification section with the approved MVP method or
  concrete blocked reason.
- [x] State which dependent questions are resolved and which remain blocked.
- [x] Ensure public/admin visibility of verification status is not implicitly
  exposed.
- [x] Confirm the diff contains only intended decision-record documentation
  changes.
- [x] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 7: Decide custom code MVP permissions

**Success Criteria:**

- `docs/decisions/mvp-boundaries.md` records MVP permissions for custom CSS,
  custom HTML, custom JavaScript, external embeds, and server-side custom code
  as approved boundaries or blocked with concrete reasons.
- If a category is forbidden in MVP, the record states that prohibition as an
  approved boundary.
- If a category is allowed in MVP, the record states required sanitization,
  sandboxing, CSP, review, storage, preview, publication, rollback, and audit
  controls before implementation.
- The record does not approve storage, execution, rendering, or public exposure
  for any custom-code category without corresponding controls.
- No source code, runtime config, dependency, concrete storage, or migration
  file is changed.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely file: `docs/decisions/mvp-boundaries.md`.
- Existing pattern: the current `## Custom Code Permissions` section lists
  custom CSS, HTML, JavaScript, external embeds, and server-side custom code.
- Decision shape sketch: convert each capability row to either approved MVP
  boundary with controls or blocked reason.
- Assertion sketch: verify no custom-code category remains ambiguous or appears
  approved without controls.

**Actions:**

- [x] Update the Custom Code Permissions section with approved MVP permissions
  or concrete blocked reasons for each category.
- [x] Record required controls for any allowed category.
- [x] Cross-check custom-code audit wording against the Audit And Events decision
  from Task 5.
- [x] Confirm the diff contains only intended decision-record documentation
  changes.
- [x] Run `rtk make quality`, fix all failures, and repeat until successful.
