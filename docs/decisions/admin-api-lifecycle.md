# Admin API Lifecycle Decision Gate

## Status

Decision-first guardrail. This record does not approve route registration,
business implementation, persistence, runtime configuration, migrations, or
dependency changes.

It complements `docs/decisions/mvp-boundaries.md`, which remains the active MVP
boundary. Any unresolved item in either decision record stays
`product decision required`.

## Requested Lifecycle Surface

The requested admin showcase lifecycle surface is blocked until the decisions in
this record are approved:

| Operation | Candidate method and path | Public access | Status |
| --- | --- | --- | --- |
| Create showcase | `POST /api/v1/showcases` | Not approved | product decision required |
| List own showcases | `GET /api/v1/showcases` | Not approved | product decision required |
| Get own showcase | `GET /api/v1/showcases/{id}` | Not approved | product decision required |
| Patch draft showcase | `PATCH /api/v1/showcases/{id}` | Not approved | product decision required |
| Clone showcase | `POST /api/v1/showcases/{id}/clone` | Not approved | product decision required |
| Archive showcase | `POST /api/v1/showcases/{id}/archive` | Not approved | product decision required |
| Restore or unarchive showcase | Not selected | Not approved | product decision required |

No `HEAD`, `OPTIONS`, or CORS/preflight behavior for these admin routes is
approved. Method parity, discovery behavior, and preflight handling for the
admin lifecycle surface are `product decision required`.

## Required Product And Security Decisions

| Decision area | Current boundary |
| --- | --- |
| Admin auth model | product decision required: choose the final auth provider, token or session validation model, trusted temporary-header gateway contract, production replacement criteria, and whether any internal-admin override is allowed. |
| Current owner context | product decision required: define the authenticated admin actor, partner or tenant ownership source, and how ownership is propagated into use cases. |
| Per-method permissions | product decision required: approve create, list own, get own, patch draft, clone, archive, and restore/unarchive permissions separately. |
| Admin `HEAD` and `OPTIONS` | product decision required: decide whether these methods exist, whether they mirror protected `GET` behavior, and how CORS/preflight should be handled. |
| Admin response fields | product decision required: approve the authenticated admin response contract for ids, owner fields, public ids or slugs, titles, statuses, draft and published snapshots, timestamps, archive metadata, and restore metadata. |
| Identifier exposure | product decision required: decide which internal ids, public ids, slugs, owner ids, tenant or partner ids, and profile identifiers may be returned to authenticated admin callers. Public exposure remains not approved. |
| Persistence backend | product decision required: choose backend storage, migration strategy, ownership model, transaction boundary, and whether any in-memory-only behavior is acceptable. |
| Lifecycle statuses | product decision required: approve the status set and transition matrix for `draft`, `published`, `unpublished`, and `archived`. |
| Draft patch behavior | product decision required: define which fields are patchable in draft state and whether a draft patch may affect any published snapshot. |
| Clone behavior | product decision required: define copied fields, new status, ownership, public id or slug handling, draft and published snapshot handling, timestamps, and audit semantics. |
| Archive behavior | product decision required: define allowed source statuses, public-read consequences, snapshot retention, recovery window, and audit semantics. |
| Restore or unarchive policy | product decision required: decide whether restore/unarchive is allowed, select the final method and path, define source and target statuses, and approve conflicts with current publication or slug state. |
| Audit and events | product decision required: choose durable audit/event requirements for create, patch, clone, archive, and restore/unarchive before mutations go live. |

## Implementation Boundary

Until these decisions are approved, this record does not allow:

- registering FastAPI admin lifecycle routes;
- adding admin lifecycle endpoint schemas;
- adding or expanding lifecycle use cases for create, list, get, patch, clone,
  archive, restore, or unarchive;
- adding persistence interfaces or implementations for lifecycle storage;
- adding `src/storages`, persistence runtime settings, migrations, database
  dependencies, or audit/event dependencies;
- exposing public or admin identifiers beyond an explicitly approved response
  contract.

Future implementation plans must keep endpoints thin: one endpoint delegates to
one use case, business rules live in `src/core`, storage access goes through
core-owned interfaces, and concrete persistence belongs under `src/storages`
only after persistence decisions are approved.
