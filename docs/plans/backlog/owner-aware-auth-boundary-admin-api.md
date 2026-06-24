# Plan: Owner-Aware Auth Boundary For Admin API

## Goal

Реализовать минимальную owner-aware auth boundary для admin API: current
user/partner context, запрет чтения и изменения чужих витрин на уровне core use
cases, централизованное API exception mapping и явно зафиксированный MVP
temporary auth adapter без привязки к внешнему auth provider.

## Context

- Текущий task description взят из rendered `ralphex --plan` request:
  `Реализуй минимальную owner-aware auth boundary для admin API: current user/partner context, запрет чтения и изменения чужих витрин, централизованное exception mapping. Не привязывайся к конкретному внешнему auth provider без решения; если нужен временный adapter, явно зафиксируй его как MVP boundary.`
- Root `AGENTS.md` прочитан; других nested `AGENTS.md` в репозитории не найдено.
- `AGENTS.md` ссылается на `/Users/optikrus/.codex/RTK.md`, но этот файл отсутствует
  в текущем окружении. Доступный `/Users/kirillpydev/.codex/RTK.md` требует `rtk`
  prefix для shell-команд.
- `README.md` в репозитории отсутствует; локальные правила берутся из `AGENTS.md`,
  `pyproject.toml`, `Makefile`, `docs/plans/README.md` и
  `docs/references/examples/ralphex.md`.
- `docs/decisions/mvp-boundaries.md` прочитан: admin API сейчас заблокирован до
  выбора auth model и method permissions; этот план должен обновить decision record,
  прежде чем добавлять admin auth behavior.
- `docs/showcase-constructor-tz.md` подтверждает, что admin write-path доступен
  только авторизованным партнёрам и внутренним администраторам, а партнёр может
  видеть и редактировать только свои витрины.
- Текущий runtime минимален: `src/api/app.py::create_app` отключает docs/openapi/redoc
  и подключает только `src/api/routers.py::root_router`; `src/api/common/endpoints.py::health`
  является единственным endpoint.
- `src/api/routers.py::root_router` сейчас включает только common router; admin routers
  и live showcase admin routes отсутствуют.
- `src/di/container.py::create_container` сейчас собирает только `FastapiProvider()`;
  доменных providers, use case providers, storages, runtime config и migrations нет.
- Тестовая инфраструктура уже централизована: `src/tests/conftest.py`,
  `src/tests/fixtures.py::APIFixture`, `src/tests/helpers/api.py::APIHelper`,
  `src/tests/helpers/factory.py::FactoryHelper`.
- Через Context7 проверено актуальное Dishka FastAPI integration behavior: для
  FastAPI используются `DishkaRoute`, `FromDishka`, `FastapiProvider` и
  `setup_dishka`; request-scoped provider может принимать `fastapi.Request`.
- `Makefile` содержит реальные targets `tests`, `tests-coverage`, `lint`, `types`,
  `fix`, `quality`; plan validation использует только project-required команды ниже.
- Этот task можно выполнить без новых dependencies, runtime configuration, persistence
  backend, Alembic migrations или storage implementation. Для owner checks достаточно
  core storage interface и mocked storage в core tests.

## Product/Security Decisions

- Method auth matrix: current `GET /health -> public`; MVP
  `GET /api/v1/admin/auth/context -> temporary request-header auth`; future admin
  showcase methods from `docs/showcase-constructor-tz.md` (`GET`, `POST`, `PATCH`,
  publish/unpublish/clone/archive actions and block mutations) must require current
  admin context and are not public.
- Public read decision: no admin `GET`, `HEAD` or `OPTIONS` route is public in this
  plan. The only confirmed public route remains `GET /health`.
- Protected methods: MVP admin auth adapter reads `X-Admin-User-Id` and
  `X-Partner-Id` from the request only to establish the boundary before an external
  auth provider is selected. Missing or blank auth context returns 401 through
  centralized exception mapping.
- Public data: this plan exposes no new public data. The protected context endpoint
  may return only `userId` and `partnerId` to the authenticated admin caller so tests
  can verify request-to-context wiring.
- Identifier exposure: `userId`, `partnerId`, `showcaseId`, and `ownerPartnerId` are
  opaque admin-side identifiers in this boundary. They must not be exposed on public
  storefront routes, and emails, usernames, profile IDs, tenant/account IDs and
  internal database IDs remain not public.
- Owner mismatch behavior: MVP owner checks return 403 `SHOWCASE_ACCESS_DENIED_ERROR`
  for authenticated callers whose `partnerId` differs from the showcase
  `ownerPartnerId`. Existence-hiding behavior that returns 404 for foreign resources
  remains `product decision required`.
- Product decision required: final external auth provider, token/session validation,
  trusted gateway contract for temporary headers, internal-admin cross-partner override,
  admin `HEAD`/`OPTIONS` and CORS behavior, persistence backend, admin mutation audit
  durability, and production replacement criteria for the temporary adapter.

## Implementation Notes

- Existing pattern: all routers are composed in `src/api/routers.py::root_router`;
  `src/api/app.py::create_app` should include `root_router` and call centralized setup
  functions only.
- Existing pattern: DI-managed endpoints use `DishkaRoute` and `FromDishka[...]`.
  Request-derived current context belongs in a request-scoped Dishka provider, not in
  endpoint business logic.
- Existing pattern: core use cases own business rules and depend on interfaces. The
  owner check belongs in core use cases before returning or mutating admin showcase data.
- Expected auth provider sketch (not final code):
  ```python
  # sketch only; inspect real files before implementation
  class AdminAuthProvider(Provider):
      @provide(scope=Scope.REQUEST)
      def get_admin_context(self, request: Request) -> AdminActorContext:
          user_id = request.headers.get("X-Admin-User-Id")
          partner_id = request.headers.get("X-Partner-Id")
          if not user_id or not partner_id:
              raise AdminAuthenticationRequiredError
          return AdminActorContext(user_id=user_id, partner_id=partner_id)
  ```
- Expected owner-check sketch (not final code):
  ```python
  # sketch only; inspect real files before implementation
  showcase = await storage.get_by_id(showcase_id=showcase_id)
  if showcase.owner_partner_id != context.partner_id:
      raise ShowcaseAccessDeniedError
  return showcase
  ```
- Test assertion sketch (not final code):
  ```python
  response = self.api.get_admin_auth_context(headers={
      "X-Admin-User-Id": "admin-user-1",
      "X-Partner-Id": "partner-1",
  })
  assert response.status_code == codes.OK
  assert response.json() == {"userId": "admin-user-1", "partnerId": "partner-1"}
  ```
- Edge cases:
  - missing vs blank auth headers;
  - context route must not accept one identifier without the other;
  - owner mismatch must prevent both returning data and calling mutation storage methods;
  - not-found and access-denied errors must be mapped centrally;
  - no internal-admin override is implemented until the product/security decision exists;
  - no persistence storage implementation, runtime settings or migrations are introduced.

## Constraints

- Follow `AGENTS.md`, `docs/plans/README.md`, `docs/references/examples/ralphex.md`,
  and applicable reference files for touched layers.
- Use existing project patterns and inspect current files again before editing.
- Do not change architecture beyond the narrow auth boundary, core owner checks and
  centralized exception mapping required by this task.
- Do not add new dependencies unless the plan is amended to update both `pyproject.toml`
  and `uv.lock`.
- Do not add runtime config, persistence implementation, `src/config` or Alembic layers.
- Do not register live admin showcase routes until their request/response fields,
  use cases and persistence boundary are planned explicitly.
- Apply TDD to behavior changes: each behavior Task starts with a focused RED test,
  then minimal production code, then focused GREEN verification.
- Each Task should be small enough to finish with green validation.

## Validation Commands

- `rtk make lint`
- `rtk make types`
- `rtk make tests`
- `rtk make quality`

## Tasks

### Task 1: Record MVP admin auth boundary decision

**Success Criteria:**

- `docs/decisions/mvp-boundaries.md` explicitly records the temporary admin auth
  adapter boundary for this MVP plan.
- The decision record states that admin methods are protected, not public, and that
  `GET /health` remains the only public runtime route confirmed before this plan.
- The decision record keeps the final external auth provider, token/session model,
  trusted gateway contract, internal admin override and production replacement criteria
  as `product decision required`.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: modify `docs/decisions/mvp-boundaries.md`.
- Existing pattern: `docs/plans/completed/mvp-product-security-tech-decisions.md`
  created this decision record and uses `product decision required` for unresolved
  auth/data exposure points.
- Document shape sketch (not final content): update `## Admin API Auth` with a short
  "MVP temporary adapter" subsection and method matrix rows for protected admin methods.
- Assertion sketch (not final code): use `rtk rg -n "MVP temporary adapter|X-Admin-User-Id|X-Partner-Id|product decision required" docs/decisions/mvp-boundaries.md`.

**Actions:**

- [x] Add a focused documentation change that records the temporary request-header auth adapter as an MVP boundary.
- [x] Run `rtk rg -n "Admin API Auth|MVP temporary adapter|X-Admin-User-Id|X-Partner-Id|product decision required" docs/decisions/mvp-boundaries.md` and confirm the boundary is discoverable.
- [x] Confirm the decision record still marks the final external auth provider and internal-admin override as `product decision required`.
- [x] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 2: Add core admin context and auth exceptions

**Success Criteria:**

- Core contains immutable current admin context data with `user_id` and `partner_id`.
- Core contains auth/permission/not-found exceptions with stable `detail` values for
  centralized API mapping.
- Focused tests prove missing or blank context identifiers are rejected before API
  provider wiring depends on them.
- The focused command `rtk uv run pytest -vv -x src/tests/core/admin_auth/test_admin_context.py::TestAdminActorContext::test_rejects_blank_required_ids` fails before production code and passes after implementation.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: create `src/core/exceptions.py`, `src/core/admin_auth/__init__.py`,
  `src/core/admin_auth/schemas.py`, `src/core/admin_auth/exceptions.py`,
  `src/tests/core/admin_auth/test_admin_context.py`.
- Existing pattern: `docs/references/examples/core.md` uses `BaseExceptionError`
  and frozen dataclasses for core schemas.
- Code shape sketch (not final code): `AdminActorContext(user_id: str, partner_id: str)`
  normalizes or rejects blank identifiers through a small factory/classmethod rather than
  placing validation in FastAPI endpoints.
- Assertion sketch (not final code): constructing context with `"admin-user-1"` and
  `"partner-1"` succeeds; empty or whitespace-only values raise
  `AdminAuthenticationRequiredError`.

**Actions:**

- [ ] Add the focused RED core test for blank or missing admin context identifiers.
- [ ] Run `rtk uv run pytest -vv -x src/tests/core/admin_auth/test_admin_context.py::TestAdminActorContext::test_rejects_blank_required_ids` and confirm it fails for the expected missing module/schema.
- [ ] Implement the minimal core context schema and exceptions required for the test to pass.
- [ ] Re-run the focused test and confirm it passes.
- [ ] Perform only necessary safe refactoring and re-run the focused test.
- [ ] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 3: Wire protected current admin context through API and DI

**Success Criteria:**

- `src/api/exceptions.py` exists, registers centralized handlers through
  `setup_exception_handlers(app=app)`, and `src/api/app.py::create_app` calls it.
- A request-scoped Dishka provider builds `AdminActorContext` from `X-Admin-User-Id`
  and `X-Partner-Id`, raising the core auth exception when either value is absent or blank.
- A minimal protected `GET /api/v1/admin/auth/context` route uses `DishkaRoute` and
  `FromDishka[AdminActorContext]` only to verify current context wiring.
- API tests prove missing context returns 401 and valid context returns only
  `userId` and `partnerId`.
- The focused command `rtk uv run pytest -vv -x src/tests/api/test_admin_auth.py::TestAdminAuthContextAPI::test_missing_context_returns_unauthorized` fails before production code and passes after implementation.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: create `src/api/exceptions.py`, `src/api/admin_auth/__init__.py`,
  `src/api/admin_auth/endpoints.py`, `src/api/admin_auth/schemas.py`,
  `src/di/providers/admin_auth.py`, `src/tests/api/test_admin_auth.py`; modify
  `src/api/app.py`, `src/api/routers.py`, `src/di/container.py`,
  `src/tests/conftest.py`, `src/tests/helpers/api.py`.
- Existing pattern: `docs/references/examples/api.md` shows `DishkaRoute`,
  `FromDishka[...]`, `root_router.include_router(...)`, and centralized exception
  registration.
- Code shape sketch (not final code): router prefix `/api/v1/admin/auth`, endpoint
  `get_current_context(context: FromDishka[AdminActorContext]) -> AdminContextResponse`.
- Assertion sketch (not final code): `self.api.get_admin_auth_context()` returns
  `codes.UNAUTHORIZED`; the same helper with both headers returns `codes.OK` and the
  expected two-field JSON body.

**Actions:**

- [ ] Add the focused RED API test for missing admin context returning 401 through centralized exception mapping.
- [ ] Run `rtk uv run pytest -vv -x src/tests/api/test_admin_auth.py::TestAdminAuthContextAPI::test_missing_context_returns_unauthorized` and confirm it fails for the expected missing route/mapping/provider.
- [ ] Implement centralized exception mapping, app wiring, request-scoped auth provider and the minimal protected context endpoint.
- [ ] Add and run the focused valid-context API test with both auth headers.
- [ ] Re-run `rtk uv run pytest -vv -x src/tests/api/test_admin_auth.py` and confirm it passes.
- [ ] Perform only necessary safe refactoring and re-run the focused API test file.
- [ ] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 4: Enforce owner-aware read access in core showcase use case

**Success Criteria:**

- Core read use case retrieves an admin showcase through a core storage interface and
  returns it only when `context.partner_id == showcase.owner_partner_id`.
- Foreign owner access raises `ShowcaseAccessDeniedError` before data is returned.
- Missing showcase behavior raises or propagates `AdminShowcaseNotFoundError` without
  converting it in the use case.
- No storage implementation, runtime config or migration is added.
- The focused command `rtk uv run pytest -vv -x src/tests/core/showcases/test_get_admin_showcase_use_case.py::TestGetAdminShowcaseUseCase::test_forbids_reading_foreign_showcase` fails before production code and passes after implementation.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: create `src/core/showcases/__init__.py`,
  `src/core/showcases/schemas.py`, `src/core/showcases/exceptions.py`,
  `src/core/showcases/use_cases.py`, `src/core/storages.py`,
  `src/tests/core/showcases/test_get_admin_showcase_use_case.py`; extend
  `src/tests/helpers/factory.py` only if factory methods reduce duplication.
- Existing pattern: `docs/references/examples/core.md` keeps use cases in core and
  storage contracts as interfaces; tests use `AsyncMock(spec=StorageInterface)`.
- Code shape sketch (not final code): `GetAdminShowcaseUseCase.execute(showcase_id, context)`
  awaits `storage.get_by_id(showcase_id=showcase_id)`, compares owner, then returns the
  domain object.
- Assertion sketch (not final code): foreign owner raises `ShowcaseAccessDeniedError`
  and `storage.get_by_id.assert_awaited_once_with(showcase_id="showcase-1")`.

**Actions:**

- [ ] Add the focused RED core use case test that proves a partner cannot read another partner's showcase.
- [ ] Run `rtk uv run pytest -vv -x src/tests/core/showcases/test_get_admin_showcase_use_case.py::TestGetAdminShowcaseUseCase::test_forbids_reading_foreign_showcase` and confirm it fails for the expected missing use case/schema/interface.
- [ ] Implement the minimal core showcase schema, storage interface, exception and read use case required for the test to pass.
- [ ] Add same-owner and not-found focused tests for the read use case.
- [ ] Re-run `rtk uv run pytest -vv -x src/tests/core/showcases/test_get_admin_showcase_use_case.py` and confirm it passes.
- [ ] Perform only necessary safe refactoring and re-run the focused read use case test file.
- [ ] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 5: Enforce owner-aware mutation access in core showcase use case

**Success Criteria:**

- Core mutation use case checks current context against the existing showcase owner before
  calling any storage mutation method.
- Foreign owner mutation raises `ShowcaseAccessDeniedError` and the storage mutation method
  is not awaited.
- Same-owner mutation delegates to storage with explicit params and returns the updated
  admin showcase domain object.
- No storage implementation, runtime config or migration is added.
- The focused command `rtk uv run pytest -vv -x src/tests/core/showcases/test_update_admin_showcase_use_case.py::TestUpdateAdminShowcaseUseCase::test_forbids_updating_foreign_showcase` fails before production code and passes after implementation.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: modify `src/core/showcases/schemas.py`, `src/core/showcases/use_cases.py`,
  `src/core/storages.py`, `src/tests/helpers/factory.py`; create
  `src/tests/core/showcases/test_update_admin_showcase_use_case.py`.
- Existing pattern: use case tests keep Arrange/Act/Assert separated and use role-based
  variable names such as `storage`, `use_case`, `context`, `params`.
- Code shape sketch (not final code): `UpdateAdminShowcaseUseCase.execute(showcase_id, params, context)`
  loads existing showcase, checks owner, then calls `storage.update_draft(...)`.
- Assertion sketch (not final code): for foreign owner, assert
  `storage.update_draft.assert_not_awaited()` after `ShowcaseAccessDeniedError`.

**Actions:**

- [ ] Add the focused RED core use case test that proves a partner cannot update another partner's showcase.
- [ ] Run `rtk uv run pytest -vv -x src/tests/core/showcases/test_update_admin_showcase_use_case.py::TestUpdateAdminShowcaseUseCase::test_forbids_updating_foreign_showcase` and confirm it fails for the expected missing mutation use case/params/interface.
- [ ] Implement the minimal update params schema, storage interface method and mutation use case required for the test to pass.
- [ ] Add same-owner and not-found focused tests for the mutation use case.
- [ ] Re-run `rtk uv run pytest -vv -x src/tests/core/showcases/test_update_admin_showcase_use_case.py` and confirm it passes.
- [ ] Perform only necessary safe refactoring and re-run the focused mutation use case test file.
- [ ] Run `rtk make quality`, fix all failures, and repeat until successful.
