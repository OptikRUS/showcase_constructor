# Reference: RALPHEX workflow

This reference documents the project-local RALPHEX workflow for
`showcase_constructor`. It complements `AGENTS.md`, `docs/plans/README.md`, and
the local `.ralphex` prompt/agent files.

## Base Contract

RALPHEX plan files are executable task specs for one feature, refactor, or
documentation workflow. They do not replace `AGENTS.md`:

- read root `AGENTS.md` before creating or executing plans;
- use applicable `docs/references/examples/*.md` files for touched surfaces;
- keep plans narrower than project policy, never contradictory to it;
- stop for user confirmation when a plan and `AGENTS.md` conflict.

New plans live in:

```text
docs/plans/backlog/<feature-name>.md
```

Completed plans live in:

```text
docs/plans/completed/<feature-name>.md
```

Do not create new plans in the root of `docs/plans/` unless the user explicitly
requests that legacy location.

## Plan Shape

Use the full template in `.ralphex/prompts/make_plan.txt`.

Parser-critical requirements:

- `# Plan: <name>`
- `## Goal`
- `## Context`
- `## Product/Security Decisions` for API/auth/user-visible data changes
- optional `## Implementation Notes` for non-trivial code changes
- `## Constraints`
- `## Validation Commands`
- `## Tasks`
- `### Task N: <specific result>`
- executable actions only as `- [ ]` checkboxes inside Task sections

Validation commands for behavior work:

```bash
rtk make lint
rtk make types
rtk make tests
rtk make quality
```

## FastAPI/Dishka Planning Rules

Plan and review work around these project boundaries:

- `src/api` is delivery: FastAPI endpoints, boundary schemas, exception mapping.
- `src/api/routers.py::root_router` is the only router composition point.
- `create_app()` includes `root_router` and app-level setup only.
- Endpoint logic stays thin: auth/validation/boundary conversion/use case call.
- One endpoint delegates to one use case.
- DI-managed endpoints use `DishkaRoute` and `FromDishka[...]`.
- Raw auth payload parsing, JWT subject validation, blank/missing credential rejection
  and auth exceptions stay in `src/api/auth/*`; core context dataclasses receive
  already-validated values and must not grow `from_raw()` or normalization helpers.
- `src/core` owns business rules and depends on interfaces.
- Persistence implementations live under `src/storages`.
- Do not introduce `repositories` or `repos`.
- Transactions are managed by DI providers when a DB layer exists.
- `session.commit()` and `session.begin()` do not belong in storage or use case code.
- Tests use `src/tests/conftest.py`, `src/tests/fixtures.py`, and
  `src/tests/helpers/` instead of local app/client/container setup.
- Do not plan standalone `src/tests/config/`, `src/tests/di/`, or
  `src/tests/migrations/` infrastructure-mechanics tests. Cover settings, DI,
  and Alembic through shared fixtures plus API/storage integration or migration
  smoke tests under the relevant behavior layer.
- Protected API tests use `APIFixture.api`; no-auth scenarios use
  `APIFixture.no_auth_api` in a separate `Test*NoAuthAPI` class.

Do not plan `src/core`, `src/storages`, `src/config`, or Alembic files until a
task actually requires those layers.

## Product/Security Decisions

Plans that touch API routes, method exposure, auth/permission behavior,
schema-visible response fields, or user-visible data must include
`## Product/Security Decisions`.

The section must explicitly answer:

- which methods are public and which require token/session auth;
- whether every touched `GET`, `HEAD`, and `OPTIONS` is public;
- which response fields are public data;
- whether identifiers may be returned;
- what requirement or existing contract justifies exposure;
- which questions remain `product decision required`.

Do not infer privacy approval from the presence of a field in a plan.

Before planning, executing, or reviewing admin API, public storefront,
persistence, custom domain, audit/event, analytics/billing, or custom-code work,
read `docs/decisions/mvp-boundaries.md`. Unresolved items in that decision record
remain `product decision required`.

## Implementation Sketches

Use `## Implementation Notes` and Task-level `Implementation Sketch` sections
when examples reduce ambiguity. Keep sketches short and file-grounded.

Good references for sketches:

- `src/api/app.py::create_app`
- `src/api/routers.py::root_router`
- `src/api/common/endpoints.py::health`
- `src/di/container.py::create_container`
- `src/tests/fixtures.py::APIFixture`
- `src/tests/helpers/api.py::APIHelper`
- the relevant `docs/references/examples/*.md` file

Sketches are not final code. The executor still inspects real files, writes
RED tests before behavior changes, and adapts to the current code.

## Task Execution Guardrails

Before selecting a Task, the executor reads:

- the complete plan file;
- the current progress log;
- `rtk git status --short`.

Then it scans deterministically for unchecked checkboxes and chooses the nearest
preceding `### Task N:` section.

If the focused RED test is already green, classify the path as:

- `coverage-only` when the useful output is extra coverage;
- `stale plan` when the plan no longer matches the code.

Do not force artificial production changes.

## Review Guardrails

Reviewer agents are read-only and finding-only. They must not edit files, create
DB schema changes, add indexes, change public fields, change auth/data contracts,
create commits, or introduce global architecture rules.

Every finding must be classified as exactly one:

- correctness/security defect;
- missing test coverage;
- product decision required;
- optional performance improvement;
- simplification;
- false positive.

The orchestrator may fix only confirmed, in-scope correctness/security defects
and missing test coverage. Findings that require product decisions, public field
changes, auth/data contract changes, persistence schema changes, or global
architecture changes require plan amendment.

Simplification findings that conflict with declared boundaries are false
positives.

## Counter / Metrics Guardrail

When a plan introduces counters, metrics, denormalized counters, or database-side
updates, it must address persisted-value safety:

- update through the declared write boundary;
- use atomic/persistence-safe updates where relevant;
- refresh or synchronize values returned in the same response;
- test response value and persisted value separately when both matter;
- cover non-mutating and failed-request paths when relevant.

## Local Config

`.ralphex/config` is local RALPHEX configuration, not application configuration.
Application settings belong under the app config layer only when a runtime task
requires them.

The portable local config keys used here are:

- `executor = codex`
- `plans_dir = docs/plans`
- `move_plan_on_completion = true`
- `pass_claude_md = true`
- task/review model and iteration controls

Keep `plans_dir` at the `docs/plans` root. RALPHEX moves completed plans into
`docs/plans/completed/` relative to that root; setting `plans_dir` to
`docs/plans/backlog` creates the invalid `docs/plans/backlog/completed/`
lifecycle path. New plans are still saved to `docs/plans/backlog/` by the plan
creation prompt.

`docs/plans/backlog/completed/` must not exist in the repository. If it appears,
move every plan inside it to `docs/plans/completed/`, remove the empty invalid
directory, and treat the cleanup as part of the RALPHEX task before claiming
completion.

Do not commit tokens, chat IDs, machine-specific paths, `.env` values, progress
logs, worktrees, or debug archives.

## Transfer Matrix

Transferred without behavior change:

- backlog-to-completed plan routing;
- `PLAN_CREATED` plus `<<<RALPHEX:PLAN_READY>>>`;
- deterministic first-unchecked-checkbox task selection;
- `coverage-only` and `stale plan`;
- read-only reviewer agents and finding categories.

Adapted for this project:

- plan validation commands now use `rtk make lint`, `rtk make types`,
  `rtk make tests`, and `rtk make quality`;
- architecture checks target FastAPI endpoints, Dishka DI, `root_router`,
  clean architecture layers, `storages`, and centralized test helpers;
- persistence/counter guidance is phrased for future SQLAlchemy-style storage
  safety without assuming a current DB layer.

Skipped:

- notification tokens and local chat settings;
- source runtime artifacts and backups;
- source CI, Docker, database services, and app-specific schema checks;
- completed/backlog feature plan content from the source project.
