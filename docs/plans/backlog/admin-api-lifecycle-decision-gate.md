# Plan: Admin API Lifecycle Decision Gate

## Goal

Prepare the requested admin API lifecycle work for showcase management without
implementing blocked routes or persistence: create an explicit decision gate for
create, list own, get own, patch draft, clone, archive, and restore/unarchive,
then pin the current no-route behavior until the required product/security
decisions are approved.

## Context

- Current task description: `Реализуй admin API для lifecycle витрины: create, list own, get own, patch draft, clone, archive, restore/unarchive only if allowed, statuses draft/published/unpublished/archived. Endpoint должен вызывать один use case, business rules в core, storage через interfaces/storages.`
- `AGENTS.md`, `docs/plans/README.md`, and `docs/references/examples/ralphex.md` require RALPHEX plans under `docs/plans/backlog/`, Product/Security Decisions for API/auth/user-visible data work, checkboxes only inside `### Task N:` sections, and `rtk` commands.
- `README.md` is absent. The local project contracts verified here are `AGENTS.md`, `pyproject.toml`, `Makefile`, source files, tests, and references under `docs/references/examples/`.
- `src/api/app.py::create_app` only includes `src/api/routers.py::root_router`; it disables docs, OpenAPI, and ReDoc.
- `src/api/routers.py::root_router` currently includes only `src/api/common/endpoints.py::router`; no admin lifecycle router is registered.
- `src/api/common/endpoints.py::health` is the only confirmed live public endpoint and returns `200`.
- `src/di/container.py::create_container` currently builds only `FastapiProvider()`; no use case, auth, storage, or database providers exist.
- `src/core/public_config/schemas.py` and `src/api/public_config/schemas.py` show dataclass domain schemas plus Pydantic boundary conversion, but public config is not wired as a live route.
- `src/tests/api/test_public_config_routes.py::TestPublicConfigRouteExposure` verifies a planned-but-unapproved public config route remains `404`; reuse this decision-first route exposure pattern for admin lifecycle.
- `src/tests/fixtures.py::APIFixture`, `src/tests/helpers/api.py::APIHelper`, and `src/tests/helpers/factory.py::FactoryHelper` are the current test infrastructure patterns.
- `docs/showcase-constructor-tz.md` specifies admin operations including create, list, get, patch, publish/unpublish, clone, archive, statuses `draft`, `published`, `unpublished`, `archived`, authorized partner-only access, draft/public separation, and audit-trail expectations.
- `docs/showcase-constructor-tz.md` states restore from archive is allowed only when product policy permits it, but no concrete restore/unarchive route, status transition, or policy is defined.
- `docs/decisions/mvp-boundaries.md` is the active decision record. It blocks admin API implementation until admin auth model and method permissions are approved, and blocks persistence until backend, migration, ownership, and transaction boundaries are approved.
- The current project has no `src/storages/`, `src/config/`, Alembic migrations, database dependency, admin auth module, admin showcase domain module, storage interface for showcases, or lifecycle use cases.
- The requested implementation cannot be completed safely without product decisions for auth/current owner context, response identifiers, persistence backend, status transitions, restore/unarchive policy, and audit/event durability.

## Product/Security Decisions

- Method auth matrix: `GET /health -> public`; requested admin lifecycle routes `POST /api/v1/showcases`, `GET /api/v1/showcases`, `GET /api/v1/showcases/{id}`, `PATCH /api/v1/showcases/{id}`, `POST /api/v1/showcases/{id}/clone`, `POST /api/v1/showcases/{id}/archive`, and any restore/unarchive route are not public and require an approved admin auth model; the concrete token/session/header/provider model remains `product decision required`.
- Public read decision: no requested admin `GET`, `HEAD`, or `OPTIONS` route is public. `HEAD`/`OPTIONS` and CORS/preflight behavior for admin routes remain `product decision required`.
- Protected methods: all requested admin lifecycle methods require authenticated admin/partner context before route registration; the source of current user/partner ownership is `product decision required`.
- Public data: none from this admin lifecycle surface is public data. Authenticated admin response fields for showcase ids, owner ids, public ids/slugs, title, status, draft/published versions, timestamps, and archive/restore metadata require explicit admin response-field approval before implementation.
- Identifier exposure: public showcase identifiers, internal database ids, owner/admin identifiers, tenant/account identifiers, and profile identifiers must not be exposed publicly. Which identifiers may be returned to authenticated admin callers remains `product decision required`.
- Product decision required: choose the admin auth model; define current owner/partner context; approve per-method permissions; decide admin `HEAD`/`OPTIONS` behavior; define the admin response field contract and allowed identifiers; choose persistence backend, migration strategy, storage ownership model, and transaction boundary; approve audit/event durability for admin mutations; define the lifecycle status transition matrix; define restore/unarchive route, policy, and allowed source statuses.

## Implementation Notes

- Existing route composition pattern: `src/api/routers.py::root_router` registers feature routers; `src/api/app.py::create_app` must not import feature endpoints directly.
- Existing thin endpoint pattern reference: `docs/references/examples/api.md` shows `src/api/<domain>/endpoints.py` using `DishkaRoute`, `FromDishka[...]`, one endpoint delegating to one use case, and boundary schemas converting to/from domain data.
- Existing core pattern reference: `docs/references/examples/core.md` shows domain dataclasses, exceptions, storage interfaces owned by core, and use cases depending on interfaces rather than concrete storage.
- Existing storage pattern reference: `docs/references/examples/storages.md` requires `src/storages`, one SQL operation per method, no business logic in storage, no `session.commit()`, and domain objects returned from storage methods.
- Existing test pattern: `src/tests/api/test_public_config_routes.py::TestPublicConfigRouteExposure` proves an unapproved route is not registered by asserting `codes.NOT_FOUND` through `APIFixture` and `APIHelper`.
- Expected future endpoint shape sketch, blocked until Product/Security Decisions are approved:
  ```python
  # sketch only; inspect real files before implementation
  router = APIRouter(prefix="/api/v1/showcases", tags=["showcases"], route_class=DishkaRoute)

  @router.post("", status_code=status.HTTP_201_CREATED)
  async def create_showcase(
      body: CreateAdminShowcaseRequest,
      context: FromDishka[AdminActorContext],
      use_case: FromDishka[CreateAdminShowcaseUseCase],
  ) -> AdminShowcaseResponse:
      showcase = await use_case.execute(context=context, params=body.to_domain())
      return AdminShowcaseResponse.from_domain(showcase=showcase)
  ```
- Expected future core shape sketch, blocked until Product/Security Decisions are approved:
  ```python
  # sketch only; inspect real files before implementation
  async def execute(self, context: AdminActorContext, showcase_id: str) -> AdminShowcase:
      showcase = await self.storage.get_by_id(showcase_id=showcase_id)
      self.policy.ensure_owner(context=context, showcase=showcase)
      return showcase
  ```
- Edge cases for the future implementation plan:
  - missing, blank, or mismatched admin owner context;
  - list/get must return only own showcases;
  - patch is allowed only for draft data and must not mutate published snapshot directly;
  - clone must define copied fields, new status, owner, public id/slug behavior, and draft/published version behavior;
  - archive must define allowed source statuses and public-read consequences for published/unpublished snapshots;
  - restore/unarchive must not be implemented until product policy defines whether it is allowed and from which source statuses;
  - persistence-side updates must return synchronized values when status/version counters or timestamps are updated in storage;
  - audit/event behavior for create, patch, clone, archive, and restore/unarchive must be defined before mutation routes go live.

## Constraints

- Follow `AGENTS.md` and applicable nested instructions.
- Use existing project patterns and project references under `docs/references/examples/`.
- Do not implement live admin lifecycle routes until Product/Security Decisions are approved.
- Do not add `src/storages`, persistence runtime config, migrations, or database dependencies until persistence decisions are approved.
- Do not expose public or admin identifiers beyond the approved response-field contract.
- Do not add new dependencies unless the plan explicitly updates `pyproject.toml` and `uv.lock`.
- Endpoints must call one use case each; business rules belong in `src/core`; storage access goes through core-owned interfaces and `src/storages` implementations only after persistence is approved.
- Apply TDD to behavior changes.
- Each Task should be small enough to finish with green validation.

## Validation Commands

- `rtk make lint`
- `rtk make types`
- `rtk make tests`
- `rtk make quality`

## Tasks

### Task 1: Record admin lifecycle implementation blockers as decisions

**Success Criteria:**

- `docs/decisions/mvp-boundaries.md` or a new focused decision record under `docs/decisions/` names the requested admin lifecycle operations and states exactly which decisions must be approved before implementation.
- The decision record covers admin auth/current owner context, per-method permissions, admin `HEAD`/`OPTIONS`, response fields, identifier exposure, persistence backend/migrations, lifecycle status transitions, restore/unarchive policy, and audit/event durability.
- No FastAPI admin routes, core lifecycle use cases, storage interfaces, storage implementations, runtime config, migrations, or dependencies are added in this Task.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: `docs/decisions/mvp-boundaries.md` or create a focused `docs/decisions/admin-api-lifecycle.md`.
- Existing pattern: `docs/decisions/mvp-boundaries.md` uses tables and `product decision required` rows for blocked admin API, persistence, public data, and audit/event topics.
- Decision shape sketch: add an admin lifecycle subsection that lists requested methods and lifecycle operations, then marks unresolved implementation choices as `product decision required` instead of selecting them implicitly.
- Validation sketch: use `rtk rg -n "admin lifecycle|restore|unarchive|product decision required" docs/decisions` to verify the decision record names the blockers.

**Actions:**

- [x] Update or create the focused decision record for the admin lifecycle blockers.
- [x] Verify the decision record explicitly keeps unresolved auth, persistence, identifier, restore/unarchive, status transition, and audit items as `product decision required`.
- [x] Confirm no live admin route, storage, config, migration, or dependency file was added in this Task.
- [x] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 2: Pin unapproved admin lifecycle routes as not registered

**Success Criteria:**

- A focused API test verifies the requested admin lifecycle route surface is not accidentally registered before Product/Security Decisions are approved.
- The test covers representative create, list own, get own, patch draft, clone, archive, and restore/unarchive candidate paths without approving the final restore/unarchive route contract.
- If the focused test is already green with no production changes, classify this Task as `coverage-only`; do not force fake production changes.
- The focused command `rtk uv run pytest -vv -x src/tests/api/test_admin_showcase_lifecycle_routes.py::TestAdminShowcaseLifecycleRouteExposure::test_admin_lifecycle_routes_are_not_registered_without_decisions` passes.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: create `src/tests/api/test_admin_showcase_lifecycle_routes.py`; extend `src/tests/helpers/api.py` only if helper methods improve clarity.
- Existing pattern: `src/tests/api/test_public_config_routes.py::TestPublicConfigRouteExposure` and `src/tests/helpers/api.py::APIHelper.get_public_config`.
- Code shape sketch (not final code): use `APIFixture` and `self.api.client.request(...)` or small `APIHelper` methods to hit candidate admin lifecycle paths.
- Assertion sketch (not final code):
  ```python
  response = self.api.client.post("/api/v1/showcases", json={"title": "Draft"})
  assert response.status_code == codes.NOT_FOUND
  ```
- Restore/unarchive route sketch: test one explicitly named candidate only as a guard against accidental exposure, and state in the test name or comments that the final method/path remains a product decision.

**Actions:**

- [ ] Add the focused API exposure test for the unapproved admin lifecycle route surface.
- [ ] Run `rtk uv run pytest -vv -x src/tests/api/test_admin_showcase_lifecycle_routes.py::TestAdminShowcaseLifecycleRouteExposure::test_admin_lifecycle_routes_are_not_registered_without_decisions`.
- [ ] If the focused test passes without production changes, classify the Task as `coverage-only`.
- [ ] If the focused test fails because a live admin lifecycle route is already registered, remove only the accidental route exposure or stop for a plan amendment if the route belongs to unrelated user work.
- [ ] Re-run the focused API test and confirm it passes.
- [ ] Run `rtk make quality`, fix all failures, and repeat until successful.
