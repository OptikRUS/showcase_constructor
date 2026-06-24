# Plan: Public Config Contract Foundation

## Goal

Реализовать core/API contract foundation для public config, совместимый с
`docs/showcase-constructor-tz.md` и widgetmarket JSON: published snapshot schema,
`settings`, `blocks`, `offers.fields[]` как `{key, value, visible}`, URL params tools,
`metricsTool`, `widgetInfo`, `triggerGroups`, а также RED tests на сериализацию и запрет
draft/private fields в public shape.

## Context

- Текущий task description взят из rendered `ralphex --plan` request:
  `Реализуй core/API contract foundation для public config, совместимый с docs/showcase-constructor-tz.md и widgetmarket JSON: settings, blocks, offers fields {key,value,visible}, URL params tools, metricsTool, widgetInfo, triggerGroups, published snapshot schema. Начни с RED tests на сериализацию и запрет draft/private fields в public shape.`
- Root `AGENTS.md` прочитан; других nested `AGENTS.md` в репозитории не найдено.
- `AGENTS.md` ссылается на `/Users/optikrus/.codex/RTK.md`, но этот файл отсутствует
  в текущем окружении. Доступный `/Users/kirillpydev/.codex/RTK.md` требует `rtk`
  prefix для shell-команд.
- `README.md` в репозитории отсутствует; локальные правила берутся из `AGENTS.md`,
  `pyproject.toml`, `Makefile`, `docs/plans/README.md` и
  `docs/references/examples/ralphex.md`.
- `docs/decisions/mvp-boundaries.md` прочитан: live public storefront routes, public
  identifier model, persistence backend, custom code permissions and admin auth model
  remain `product decision required`.
- `docs/showcase-constructor-tz.md` defines public config fields under section 9.4:
  `id`, `affiliateId`, `type`, `settings`, `platform: {id}`, `blocks[]`,
  `widgetInfo`, `constantUrlParamsTool`, `transferredUrlParamsTool`, `metricsTool`,
  and `is_need_to_send_offers_display_and_positions`.
- `docs/showcase-constructor-tz.md` also states public API must read only published
  snapshot data, while drafts, owner internal IDs, service settings and private stats
  must not reach public API.
- Current app is minimal: `src/api/app.py::create_app` disables docs/openapi/redoc and
  includes only `src/api/routers.py::root_router`; `src/api/common/endpoints.py::health`
  is the only endpoint.
- `src/di/container.py::create_container` currently creates only `FastapiProvider()`;
  no `src/core`, `src/storages`, `src/config`, migrations, domain providers or use case
  providers exist yet.
- Tests are centralized through `src/tests/conftest.py`, `src/tests/fixtures.py::APIFixture`,
  `src/tests/helpers/api.py::APIHelper`, and `src/tests/api/test_health.py::TestHealthAPI`.
- `Makefile` exposes real targets `tests`, `tests-coverage`, `lint`, `types`, `fix`,
  and `quality`; plan validation uses only the required commands below.
- This task can be completed without new dependencies, runtime configuration,
  persistence, Alembic migrations, external clients or live public route registration.

## Product/Security Decisions

- Method auth matrix: existing `GET /health -> public`; no new live route is approved
  by this plan. Future `GET /api/v1/public/showcases/resolve?host=...&path=...` and
  `GET /api/v1/public/showcases/{public_id}` remain `product decision required` for
  public method exposure until route, cache and identifier decisions are approved.
- Public read decision: this plan may add core schemas and API boundary response schemas
  for public config serialization tests only; it must not register public `GET`, `HEAD`
  or `OPTIONS` routes in `src/api/routers.py`.
- Protected methods: public config contract foundation contains no mutations. Future
  admin `POST`/`PUT`/`PATCH`/`DELETE` and management reads remain blocked by the admin
  auth model decision in `docs/decisions/mvp-boundaries.md`.
- Public data: schema candidates are limited to the public published snapshot shape
  required by `docs/showcase-constructor-tz.md`: `id`, `affiliateId` only as a CPA/public
  affiliate identifier, `type`, `settings`, `platform.id`, `blocks`, `widgetInfo`,
  `constantUrlParamsTool`, `transferredUrlParamsTool`, `metricsTool`,
  `is_need_to_send_offers_display_and_positions`, `offers`, `triggerGroups`, and offer
  fields `{key, value, visible}`.
- Identifier exposure: public config `id` must represent an opaque public showcase/widget
  config id from the published snapshot, not an internal database id. Owner/admin emails,
  usernames, profile IDs, tenant/account IDs, draft version IDs, internal block/offer IDs,
  service settings and private stats are forbidden in the public response shape.
- Product decision required: live public route exposure, lookup by `public_id`, domain/path
  resolution, cache invalidation, persistence backend, custom code exposure, and whether
  `affiliateId` is safe as public tracking data before any runtime public API is exposed.

## Implementation Notes

- Existing pattern: `src/api/routers.py::root_router` is the only router composition point;
  this plan must not add a public router until Product/Security Decisions approve it.
- Existing pattern: `docs/references/examples/core.md` uses frozen dataclasses under
  `src/core/<domain>/schemas.py`; create `src/core/public_config/schemas.py` only because
  the task requires core public config contract objects.
- Existing pattern: `docs/references/examples/api.md` defines `src/api/boundary.py` with a
  Pydantic `BoundaryModel`; use it for camelCase public JSON aliases, with an explicit alias
  for the required snake_case flag `is_need_to_send_offers_display_and_positions`.
- Existing pattern: domain factories belong in `src/tests/helpers/factory.py` and mixins in
  `src/tests/fixtures.py` when domain objects are needed in tests.
- Expected response shape sketch (not final code):
  ```python
  public_config = PublicConfigResponse.from_domain(snapshot=snapshot)
  payload = public_config.model_dump(mode="json", by_alias=True)
  assert payload["widgetInfo"]["triggerGroups"][0]["type"] == "page_open"
  assert payload["widgetInfo"]["offers"][0]["fields"] == [
      {"key": "amount", "value": "100000", "visible": True},
  ]
  ```
- Draft/private field assertion sketch (not final code):
  ```python
  dumped = public_config.model_dump(mode="json", by_alias=True)
  assert "ownerId" not in dumped
  assert "draftVersion" not in dumped
  assert "privateStats" not in dumped
  assert "internalId" not in dumped["widgetInfo"]["offers"][0]
  ```
- Edge cases:
  - public config uses mostly camelCase JSON, but the analytics flag remains
    `is_need_to_send_offers_display_and_positions`;
  - hidden offer fields are still represented as `{key, value, visible}` unless the
    executor verifies a stricter product rule before implementation;
  - missing optional blocks or `widgetInfo` must serialize predictably without reading
    draft data;
  - no storage interface, runtime config or Alembic migration is planned.

## Constraints

- Follow `AGENTS.md`, `docs/plans/README.md`, `docs/references/examples/ralphex.md`,
  and applicable reference files for touched layers.
- Use existing project patterns and real files; inspect current files again before editing.
- Do not change architecture beyond the narrow `core/public_config` and
  `api/public_config` contract foundation required by this task.
- Do not add new dependencies unless the plan is amended to update both `pyproject.toml`
  and `uv.lock`.
- Do not add runtime config, persistence, `src/storages`, `src/config` or Alembic layers.
- Do not register live public routes until public method, identifier and field exposure
  decisions are approved.
- Apply TDD to behavior changes: each Task starts with a focused RED test, then minimal
  production code, then focused GREEN verification.
- Each Task must be small enough to finish with green validation.

## Validation Commands

- `rtk make lint`
- `rtk make types`
- `rtk make tests`
- `rtk make quality`

## Tasks

### Task 1: Add core published public config schema

**Success Criteria:**

- `src/core/public_config/schemas.py` defines immutable public config domain objects for
  published snapshot data, including settings, blocks, widget info, URL params tools,
  metrics tool, trigger groups, offers, and offer fields `{key, value, visible}`.
- `src/tests/core/public_config/test_public_config_schemas.py` proves the domain object can
  represent the widgetmarket public shape without draft/private fields.
- The focused command `rtk uv run pytest -vv -x src/tests/core/public_config/test_public_config_schemas.py::TestPublishedPublicConfigSnapshot::test_public_shape_contains_widgetmarket_fields` fails before production code and passes after implementation.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: create `src/core/public_config/__init__.py`,
  `src/core/public_config/schemas.py`, `src/tests/core/public_config/test_public_config_schemas.py`;
  create `src/tests/helpers/factory.py` and extend `src/tests/fixtures.py` with
  `FactoryFixture` if domain factories are needed.
- Existing pattern: `docs/references/examples/core.md` uses frozen dataclasses with
  `slots=True`; `docs/references/examples/tests.md` keeps tests inside `class Test*`.
- Code shape sketch (not final code): dataclasses such as `PublicOfferField`,
  `PublicOffer`, `PublicWidgetInfo`, `PublicBlock`, `UrlParamsTool`, `MetricsTool`,
  `PublicConfigSettings`, and `PublishedPublicConfigSnapshot`.
- Assertion sketch (not final code): build a factory snapshot and assert it exposes
  `settings`, `blocks`, `widget_info.offers[0].fields[0].key == "amount"`, and
  `widget_info.trigger_groups[0].type == "page_open"`.

**Actions:**

- [x] Add the focused RED core test for the published public config snapshot shape.
- [x] Run `rtk uv run pytest -vv -x src/tests/core/public_config/test_public_config_schemas.py::TestPublishedPublicConfigSnapshot::test_public_shape_contains_widgetmarket_fields` and confirm it fails for the expected missing module/schema.
- [x] Implement the minimal immutable core dataclasses needed for the test to pass.
- [x] Re-run the focused test and confirm it passes.
- [x] Perform only necessary safe refactoring and re-run the focused test.
- [x] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 2: Add API boundary serialization for widgetmarket JSON

**Success Criteria:**

- `src/api/boundary.py` provides the project boundary model pattern from
  `docs/references/examples/api.md` if it does not already exist.
- `src/api/public_config/schemas.py` converts the core published snapshot to JSON-compatible
  response schemas with widgetmarket field names: `affiliateId`, `platform`, `widgetInfo`,
  `constantUrlParamsTool`, `transferredUrlParamsTool`, `metricsTool`, `triggerGroups`, and
  `is_need_to_send_offers_display_and_positions`.
- `src/tests/api/test_public_config_schemas.py` proves `model_dump(mode="json", by_alias=True)`
  emits the expected public JSON and keeps offer fields as `{key, value, visible}`.
- The focused command `rtk uv run pytest -vv -x src/tests/api/test_public_config_schemas.py::TestPublicConfigResponseSchema::test_serializes_widgetmarket_json` fails before production code and passes after implementation.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: create `src/api/boundary.py`, `src/api/public_config/__init__.py`,
  `src/api/public_config/schemas.py`, and `src/tests/api/test_public_config_schemas.py`.
- Existing pattern: API schemas use classmethods like `from_domain(...)` in
  `docs/references/examples/api.md`.
- Code shape sketch (not final code): `PublicConfigResponse.from_domain(snapshot=...)`
  maps snake_case domain fields to Pydantic response models; the analytics flag uses
  an explicit alias because generic camelCase conversion would produce the wrong key.
- Assertion sketch (not final code): compare the serialized dict to a compact expected
  widgetmarket payload containing settings, one block, one widget offer, URL param tools,
  metrics tool, and trigger groups.

**Actions:**

- [x] Add the focused RED API serialization test for widgetmarket JSON aliases and nested fields.
- [x] Run `rtk uv run pytest -vv -x src/tests/api/test_public_config_schemas.py::TestPublicConfigResponseSchema::test_serializes_widgetmarket_json` and confirm it fails for the expected missing schema.
- [x] Implement the minimal boundary model and public config response schemas required for the test to pass.
- [x] Re-run the focused test and confirm it passes.
- [x] Perform only necessary safe refactoring and re-run the focused test.
- [x] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 3: Reject draft and private fields in public API shape

**Success Criteria:**

- API serialization tests prove draft/private fields cannot leak into the public shape,
  including owner/admin identifiers, tenant/account identifiers, draft version data,
  internal IDs, service settings and private stats.
- Response schemas either ignore untrusted extra input during explicit construction from
  the core public snapshot or forbid extras where the executor verifies that is safer for
  the local Pydantic pattern.
- The focused command `rtk uv run pytest -vv -x src/tests/api/test_public_config_schemas.py::TestPublicConfigResponseSchema::test_excludes_draft_and_private_fields` fails before production code and passes after implementation.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: modify `src/api/public_config/schemas.py` and
  `src/tests/api/test_public_config_schemas.py`; modify `src/core/public_config/schemas.py`
  only if the core public snapshot needs an explicit projection helper.
- Existing pattern: endpoints should call one use case and convert through boundary schemas,
  but this task intentionally does not add an endpoint because public route exposure is
  still `product decision required`.
- Code shape sketch (not final code): keep public schemas allowlisted by field definition and
  avoid dict passthrough from draft/admin data structures.
- Assertion sketch (not final code): serialize a public snapshot built near fake draft/private
  source data and assert none of `ownerId`, `tenantId`, `draftVersion`, `privateStats`,
  `serviceSettings`, `createdBy`, `internalId` appear at top level or inside nested offers.

**Actions:**

- [x] Add the focused RED API test that attempts to leak draft/private field names into public serialization.
- [x] Run `rtk uv run pytest -vv -x src/tests/api/test_public_config_schemas.py::TestPublicConfigResponseSchema::test_excludes_draft_and_private_fields` and confirm it fails for the expected missing guard or schema behavior.
- [x] Implement the minimal allowlisted serialization behavior required for the test to pass.
- [x] Re-run the focused test and confirm it passes.
- [x] Perform only necessary safe refactoring and re-run the focused test.
- [x] Run `rtk make quality`, fix all failures, and repeat until successful.

### Task 4: Keep the contract foundation unexposed by runtime routing

**Success Criteria:**

- `src/api/routers.py::root_router` still registers only approved routers unless a later
  Product/Security Decision explicitly approves public config routes.
- A focused API test verifies `GET /api/v1/public/showcases/example` is not accidentally
  exposed by this foundation work.
- No Dishka provider, storage interface, runtime config or migration is added for public
  config contract schemas.
- The focused command `rtk uv run pytest -vv -x src/tests/api/test_public_config_routes.py::TestPublicConfigRouteExposure::test_public_config_route_is_not_registered_without_decision` fails only if a route is accidentally registered and passes after preserving the routing boundary.
- `rtk make quality` exits successfully.

**Implementation Sketch:**

- Likely files: create `src/tests/api/test_public_config_routes.py`; modify
  `src/tests/helpers/api.py` only if adding an `APIHelper.get_public_config(...)` method
  keeps the test aligned with existing helper patterns.
- Existing pattern: `src/tests/api/test_health.py::TestHealthAPI` uses `APIFixture` and
  `APIHelper`, and `src/api/routers.py` is the only router composition point.
- Code shape sketch (not final code): use the existing no-auth client through `APIHelper`
  and assert the unapproved public config path returns `codes.NOT_FOUND`.
- Assertion sketch (not final code): `assert response.status_code == codes.NOT_FOUND`.

**Actions:**

- [x] Add the focused route exposure test using existing API fixture/helper patterns.
- [x] Run `rtk uv run pytest -vv -x src/tests/api/test_public_config_routes.py::TestPublicConfigRouteExposure::test_public_config_route_is_not_registered_without_decision` and confirm it passes with the current routing boundary.
- [x] If the test unexpectedly fails because a route exists, stop and classify the route exposure as `product decision required` before changing app behavior (not triggered; focused route test passed).
- [x] Confirm no public config router is included from `src/api/routers.py`.
- [x] Run `rtk make quality`, fix all failures, and repeat until successful.
