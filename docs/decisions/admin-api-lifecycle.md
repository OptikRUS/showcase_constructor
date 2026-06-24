# Admin API Lifecycle Decision Gate

## Status

Decision-first guardrail. This record does not approve route registration,
business implementation, persistence, runtime configuration, migrations, or
dependency changes.

It complements `docs/decisions/mvp-boundaries.md`, which remains the active MVP
boundary. The admin showcase route/auth boundary below is approved for MVP
planning, while any unresolved item in either decision record stays
`product decision required`.

## Approved Lifecycle Surface

The requested admin showcase lifecycle surface is approved only as a protected,
owner-scoped admin boundary. No admin showcase route is public. Every approved
route must resolve the current `AdminActorContext` through the MVP JWT bearer
adapter, and use cases must return or mutate only showcases whose
`owner_partner_id` matches `context.partner_id`.

| Operation | Candidate method and path | Public access | Status |
| --- | --- | --- | --- |
| Create showcase | `POST /api/v1/showcases` | Not approved | Approved MVP boundary: authenticated current admin context required; created showcase belongs to `context.partner_id`. |
| List own showcases | `GET /api/v1/showcases` | Not approved | Approved MVP boundary: authenticated current admin context required; response is limited to showcases owned by `context.partner_id`. |
| Get own showcase | `GET /api/v1/showcases/{id}` | Not approved | Approved MVP boundary: authenticated current admin context required; foreign-partner showcases must not be returned. |
| Patch draft showcase | `PATCH /api/v1/showcases/{id}` | Not approved | Approved MVP boundary: authenticated current admin context required; only owned draft data may be patched. |
| Clone showcase | `POST /api/v1/showcases/{id}/clone` | Not approved | Approved MVP boundary: authenticated current admin context required; source and clone must belong to `context.partner_id`. |
| Archive showcase | `POST /api/v1/showcases/{id}/archive` | Not approved | Approved MVP boundary: authenticated current admin context required; only owned showcases may be archived. |
| Restore showcase | `POST /api/v1/showcases/{id}/restore` | Not approved | Approved MVP boundary: authenticated current admin context required; only owned archived showcases may be restored. |
| Unarchive showcase alias | `POST /api/v1/showcases/{id}/unarchive` | Not approved | Blocked: MVP selects `restore` as the single recovery verb to avoid duplicate route semantics. |

`HEAD` routes are intentionally not app-defined for the admin lifecycle MVP.
They do not mirror admin `GET` responses, do not expose public metadata, and
must remain unregistered unless a later decision approves explicit admin
metadata behavior.

`OPTIONS` routes are intentionally not app-defined as admin business routes for
the MVP. If CORS/preflight support is introduced later, it must be handled as
application middleware/infrastructure and must not make admin resources public.

## Required Product And Security Decisions

| Decision area | Current boundary |
| --- | --- |
| Admin auth model | MVP JWT bearer adapter selected for current-context wiring; external auth-provider integration, refresh/session activation, production replacement criteria, and internal-admin override remain product decision required. |
| Current owner context | JWT subject must provide `user_id` and `partner_id`; approved lifecycle routes must pass the already-validated current admin context to one use case and enforce `context.partner_id` ownership before returning or mutating showcase data. |
| Per-method permissions | Approved MVP boundary for create, list own, get own, patch draft, clone, archive, and restore through the method/path matrix above; `unarchive` alias remains blocked. |
| Admin `HEAD` and `OPTIONS` | Approved MVP boundary: no app-defined admin lifecycle `HEAD` or `OPTIONS` routes. Future CORS middleware must not change admin resource visibility. |
| Admin response fields | Approved and blocked field groups are defined in `Authenticated Admin Response Boundary` below. |
| Identifier exposure | Authenticated admin `id` and `ownerPartnerId` may be returned only for owned admin resources. `publicId` may be returned only as the opaque public showcase id approved in `docs/decisions/mvp-boundaries.md`; public slugs remain blocked. Public storefront route exposure remains not approved. |
| Persistence backend | product decision required: choose backend storage, migration strategy, ownership model, transaction boundary, and whether any in-memory-only behavior is acceptable. |
| Lifecycle statuses | Approved response boundary may expose `draft`, `published`, `unpublished`, and `archived` status values; the full transition matrix remains product decision required for behavior implementation. |
| Draft patch behavior | product decision required: define which fields beyond the current `title` draft update are patchable and whether a draft patch may affect any published snapshot. |
| Clone behavior | product decision required: define copied fields, new status, public id or slug handling, draft and published snapshot handling, and timestamps. Ownership is approved as `context.partner_id`; audit emission follows the process-local in-memory boundary in `docs/decisions/mvp-boundaries.md`. |
| Archive behavior | product decision required: define allowed source statuses, public-read consequences, snapshot retention, and recovery window. Audit emission follows the process-local in-memory boundary in `docs/decisions/mvp-boundaries.md`. |
| Restore policy | product decision required: define source and target statuses, recovery window, and conflicts with current publication or slug state for `POST /api/v1/showcases/{id}/restore`. Audit emission follows the process-local in-memory boundary in `docs/decisions/mvp-boundaries.md`. |
| Audit and events | Approved MVP boundary: owner-scoped create, patch draft, clone, archive, and restore mutations must emit process-local in-memory audit records as defined in `docs/decisions/mvp-boundaries.md`. Durable audit, outbox events, external streams, and the blocked `unarchive` alias remain product decision required. |

## Authenticated Admin Response Boundary

This response boundary applies only to authenticated admin callers after the
owner check succeeds. It does not approve public storefront exposure.

| Field group | Authenticated admin response boundary |
| --- | --- |
| Showcase `id` | Approved MVP boundary as the admin resource identifier used in admin route paths and responses. It is not a public showcase identifier. Direct database primary-key shape remains tied to the later persistence decision. |
| Owner and partner fields | `ownerPartnerId` is approved only when it equals the caller's `context.partner_id`. Owner/admin emails, usernames, profile identifiers, and cross-partner account identifiers are blocked. |
| Public ids or slugs | `publicId` is approved only as the opaque public showcase id defined in `docs/decisions/mvp-boundaries.md`, and only for owned admin resources. Public slugs, custom-domain identifiers, domain plus path aliases, and internal database ids remain blocked. |
| Title | Approved MVP boundary for create, list own, get own, patch draft, clone, archive, and restore responses. |
| Status | Approved MVP boundary for admin-owned resources using `draft`, `published`, `unpublished`, and `archived`; transition rules remain behavior decisions. |
| Draft snapshot metadata | Approved MVP boundary for metadata needed by the owner, such as draft version, update timestamp, and dirty/published comparison flags. Draft snapshot content fields remain tied to later constructor editing decisions. |
| Published snapshot metadata | Approved MVP boundary for metadata needed by the owner, such as published version, publication timestamp, and whether a published snapshot exists. Public snapshot field exposure is governed by the approved published snapshot response-field boundary in `docs/decisions/mvp-boundaries.md`; public route registration remains separate. |
| Timestamps | `createdAt` and `updatedAt` are approved MVP response fields for authenticated owner-scoped admin routes. |
| Archive metadata | `archivedAt` is approved when archive behavior is implemented. `archivedBy` actor identifiers and retention/recovery details remain blocked until audit and archive behavior decisions are approved. |
| Restore metadata | `restoredAt` is approved when restore behavior is implemented. `restoredBy` actor identifiers and conflict-resolution details remain blocked until audit and restore behavior decisions are approved. |
| Private/internal fields | Draft-private settings, service credentials, audit internals, storage implementation details, tenant/account identifiers unrelated to the current owner boundary, and foreign-owner data are blocked. |

## Implementation Boundary

This record still does not directly implement or register routes. Future
implementation plans may use the approved method/auth/response boundary above,
but must also satisfy any still-unresolved persistence, lifecycle behavior,
public route method/path, and durable audit/event decisions before the
corresponding behavior goes live. Public identifiers and public response fields
must follow the opaque public showcase id and published snapshot response-field
boundaries in `docs/decisions/mvp-boundaries.md`. Test/demo admin mutations must
use that record's process-local in-memory audit/event boundary.

This record does not allow:

- adding persistence interfaces or implementations for lifecycle storage;
- adding `src/storages`, persistence runtime settings, migrations, database
  dependencies, or audit/event dependencies;
- exposing public slugs, public storefront data outside the approved published
  snapshot boundary, foreign-owner data, internal database ids, or admin
  identifiers beyond the authenticated admin response contract above.

Future implementation plans must keep endpoints thin: one endpoint delegates to
one use case, business rules live in `src/core`, storage access goes through
core-owned interfaces, and concrete persistence belongs under `src/storages`
only after persistence decisions are approved.
