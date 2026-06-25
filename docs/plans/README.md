# RALPHEX Plans

This directory contains executable RALPHEX plan files for `showcase_constructor`.

## Project Rules

- Read `AGENTS.md` before writing or executing a plan.
- Keep one feature, refactor, or documentation workflow per plan file.
- Store new plans as `docs/plans/backlog/<feature-name>.md`.
- Only the orchestrator archives completed plans to `docs/plans/completed/`.
- Keep RALPHEX `plans_dir` pointed at `docs/plans`, not
  `docs/plans/backlog`; otherwise completed plans are archived into the invalid
  `docs/plans/backlog/completed/` subtree.
- Treat any existing `docs/plans/backlog/completed/` directory as a repository
  hygiene failure. Planning, task, and review agents report it as a blocker
  instead of moving or editing unrelated plans.
- Active failed plans remain in `docs/plans/backlog/` until the orchestrator
  explicitly archives them.
- The orchestrator archives only after review fixes are committed and
  `rtk git status --short` is clean.
- Use `rtk` for shell commands.
- Do not add dependencies unless the plan explicitly updates both `pyproject.toml`
  and `uv.lock`.
- Do not plan standalone `src/tests/config/`, `src/tests/di/`, or
  `src/tests/migrations/` tests for settings, DI, or Alembic mechanics. Use
  shared fixtures/helpers and layer-level API/storage integration smoke tests.
- Do not commit unless the user explicitly asks, except inside an active RALPHEX
  execution loop where the task prompt requires committing the completed Task.
- Prefer `ralphex --worktree docs/plans/backlog/<feature-name>.md` for feature
  work when autonomous execution should be isolated from the current checkout.

## Plan Creation Notes

For `ralphex --plan "<task description>"`, the current request must come from
the rendered prompt or current `.ralphex/progress/progress-plan*.txt` log. If
the task text is not visible in the prompt, recover it from the first
`plan request: <text>` line before asking the user.

Existing plan files are style examples only, not fallback task descriptions.
Do not use active, completed, backlog, or untracked plan files as the source
task. Only this README may be read before resolving the current request.

Make-plan changes only the newly created `docs/plans/backlog/<feature-name>.md`
plan file. Unrelated plan lifecycle or hygiene problems are blockers for the
plan-creation run, not cleanup work for the planning agent.

Plans should include compact implementation sketches when they reduce ambiguity
for non-trivial code changes. Sketches are not final code. They must point to
verified project files or patterns and must not replace TDD or fresh inspection
during execution.

For plans that change API routes, auth/permission behavior, method exposure,
schema-visible response fields, or other user-visible data, include a required
`## Product/Security Decisions` section.

## Required Plan Shape

Each plan must include:

- `# Plan: <feature-name>`
- `## Goal`
- `## Context`
- `## Product/Security Decisions` for API/auth/user-visible data changes
- optional `## Implementation Notes` for non-trivial code changes
- `## Constraints`
- `## Validation Commands`
- `## Tasks`
- one or more `### Task N: <task-name>` sections
- task actions as checkboxes under each Task section

Use checkboxes only inside Task sections. RALPHEX treats unchecked boxes as task
work, so do not place checkboxes in intro, context, or validation sections.

## Product/Security Decisions

The section must answer:

- method auth matrix for each touched route;
- whether each touched `GET`, `HEAD`, and `OPTIONS` path is public;
- which methods require token/session auth;
- which response fields are public data;
- whether identifiers may be returned and why;
- which unresolved questions remain `product decision required`.

Do not infer privacy approval only because a field appears in a plan. Missing or
disputed auth/data exposure requires a plan amendment before implementation.

Before planning, executing, or reviewing admin API, public storefront,
persistence, custom domain, audit/event, analytics/billing, or custom-code work,
read `docs/decisions/mvp-boundaries.md`. Unresolved items in that decision record
remain `product decision required`.

## Task Sizing

Each Task should be one cohesive vertical milestone that RALPHEX can finish in
one iteration. A Task is not a micro-step by default; it usually covers 2-4
tightly related observable results when they belong to one capability, one
auth/publicness decision, one domain aggregate, and one family of tests.

For a medium feature, aim for roughly 3-5 Task sections. For a large feature,
aim for roughly 5-7 Task sections. Do not split every endpoint, method, or helper
into its own Task when the work is one reviewable capability slice.

It is acceptable to combine list/create plus patch/delete for one draft resource
when owner checks, schemas, storage, use cases, validation, and tests are one
cohesive slice.

Split Tasks across different Product/Security Decisions, public and protected
API, schema migration and behavioral API slices, unrelated domains, different
persistence boundaries, or review-only work and production behavior.

Success Criteria must enumerate every scenario inside the milestone. Actions
remain TDD-oriented for behavior work: add the focused tests, observe the
expected RED, make the minimal implementation, reach GREEN, refactor only as
needed, and run the required validation. Do not add a final catch-all testing
Task.

## Task Selection

Task execution starts by reading the whole plan, the current progress log, and
`rtk git status --short`. Only after that should an executor scan for the first
unchecked checkbox and select the nearest preceding `### Task N:` section.

Task agents update only the selected plan's current Task checkboxes and the
current task implementation. They do not move active, failed, or completed plan
files.

If the focused RED test for the selected Task is already green before production
changes, do not invent a production diff. Mark the path as `coverage-only` when
extra coverage is useful, or `stale plan` when the plan no longer matches code.

## Review Guardrails

Reviewer agents are read-only and finding-only. They may inspect diffs, source,
plans, and docs, but must not edit files, create DB schema changes, add indexes,
change public fields, change auth/data contracts, add global architecture rules,
or commit.

Review agents and review-fix passes do not archive or move plan files. A dirty
worktree, uncommitted review fixes, or unrelated plan lifecycle artifact blocks
review completion until the orchestrator handles it.

Every review finding must be classified before action as exactly one of:
`correctness/security defect`, `missing test coverage`, `product decision required`,
`optional performance improvement`, `simplification`, or `false positive`.

The review orchestrator may fix only confirmed, in-scope
`correctness/security defect` and `missing test coverage` findings. Public
response fields, auth/data contract changes, persistence schema changes, and
global architecture rules require an explicit plan amendment.

## Validation Commands

For backend or API changes, include:

```bash
rtk make lint
rtk make types
rtk make tests
rtk make quality
```

For documentation-only or RALPHEX configuration changes, include artifact checks
plus the project quality gate when realistic:

```bash
rtk rg --files .ralphex docs/plans docs/references/examples
rtk rg -n "^### Task|^- \\[ \\]" docs/plans .ralphex/prompts
rtk ralphex --config-dir=.ralphex --version
rtk make quality
```

## Verify After Save

After creating or editing a plan artifact, verify that the file exists, Task
headers are discoverable, checkboxes are only in Task sections, and the diff is
scoped:

```bash
rtk ls docs/plans/backlog/<feature-name>.md
rtk rg -n "^### Task|^- \\[ \\]" docs/plans/backlog/<feature-name>.md
rtk test ! -d docs/plans/backlog/completed
rtk git diff HEAD -- docs/plans/backlog/<feature-name>.md
rtk git status --short
```
