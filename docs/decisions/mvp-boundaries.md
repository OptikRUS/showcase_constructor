# MVP Boundaries

## Scope

This record is the current decision boundary for the showcase constructor MVP. It
does not approve business implementation, new routes, durable persistence,
runtime configuration, migrations, or custom rendering behavior.

### In scope

- The existing `GET /health` endpoint remains the only confirmed public runtime
  surface.
- Decision-first planning for constructor scope, showcase publishing, custom
  domains, analytics, billing, admin API, public storefront behavior, and custom
  code permissions.
- Future feature plans may reference this record to decide whether work is
  unblocked or must stop as `product decision required`.

### Out of scope

- Implementing business code, FastAPI endpoints, DI providers, storages,
  settings, migrations, or external clients in this decision-first task.
- Treating constructor editing, showcase publishing, custom domains, analytics,
  billing, full admin API behavior, or public storefront behavior as approved
  MVP features.
- Exposing internal database IDs, admin emails, usernames, profile identifiers,
  tenant/account identifiers, custom code metadata, or verification status before
  a later decision explicitly approves each field.
- Adding dependencies or new architecture layers before a feature plan requires
  them and updates the project artifacts that govern them.

## MVP Boundary Decisions

| Area | MVP boundary | Status |
| --- | --- | --- |
| Constructor editing | product decision required | Blocked until the editable entities, permissions, and publishing workflow are approved. |
| Showcase publishing | product decision required | Blocked until publication states, public fields, and rollback needs are approved. |
| Custom domains | product decision required | Blocked until domain ownership verification and failure handling are approved. |
| Analytics | product decision required | Blocked until event collection, retention, and public/admin visibility are approved. |
| Billing | product decision required | Blocked until paid features, account ownership, and provider integration are approved. |
| Admin API | MVP JWT bearer adapter plus approved admin showcase route boundary | `docs/decisions/admin-api-lifecycle.md` approves protected owner-scoped create, list own, get own, patch draft, clone, archive, and restore route boundaries; storage, lifecycle behavior, published-snapshot exposure, and audit durability still require their focused decisions. |
| Public storefront | Opaque public showcase id approved; route and field exposure product decision required | Future public reads may address a published snapshot by opaque public showcase id only. Public route registration, methods, and response fields remain blocked until their focused decisions are approved. |
| Persistence | Approved in-memory MVP storage boundary; durable persistence product decision required | Future MVP implementation may add only process-local, non-durable `src/storages` storage for admin showcase flows. Database/file/external persistence, runtime config, migrations, and durability claims remain blocked until a durable backend decision is approved. |
| Custom code | product decision required | Blocked until allowed code categories, sanitization, sandboxing, and review rules are approved. |

## Admin API Auth

### MVP JWT bearer adapter

This MVP boundary uses a `fastapi-jwt` bearer token adapter to establish the
owner-aware admin boundary. The JWT subject must contain `user_id` and
`partner_id`; missing, invalid, or blank values are unauthenticated.

The JWT adapter may protect `GET /api/v1/admin/auth/context` and future admin
showcase use cases that consume the current admin context. It does not approve
public admin data exposure and does not approve an internal-admin cross-partner
override.

External auth-provider integration, refresh/session activation, internal-admin
override, and production replacement criteria remain `product decision required`.

Admin showcase lifecycle method/auth boundaries are approved in
`docs/decisions/admin-api-lifecycle.md` for protected owner-scoped create, list
own, get own, patch draft, clone, archive, and restore routes. That focused
record selects `POST /api/v1/showcases/{id}/restore` for recovery and keeps the
`unarchive` alias blocked. Storage, lifecycle behavior, published-snapshot
exposure, and audit durability remain governed by their focused decisions before
implementation may go live. Public identifiers use the opaque public showcase id
boundary below; slugs and custom-domain identifiers remain blocked.

The only confirmed public runtime route remains `GET /health`. No admin `GET`,
`HEAD`, `OPTIONS`, `POST`, `PUT`, `PATCH`, or `DELETE` route is public in this
MVP boundary unless a later decision record explicitly approves that method,
path, and rationale.

| Surface | Method class | Public access | Required auth | Status |
| --- | --- | --- | --- | --- |
| Admin current context | `GET /api/v1/admin/auth/context` | Not approved | MVP JWT bearer adapter | Approved only for protected request-to-context wiring. |
| Admin management reads | `GET /api/v1/showcases`, `GET /api/v1/showcases/{id}` | Not approved | Current admin context required | Approved only for owner-scoped list/get boundaries in `docs/decisions/admin-api-lifecycle.md`. |
| Admin read metadata | `HEAD` | Not approved | Not app-defined | Approved MVP boundary: no explicit admin lifecycle `HEAD` routes. |
| Admin preflight/discovery | `OPTIONS` | Not approved | Not app-defined as admin business routes | Approved MVP boundary: no explicit admin lifecycle `OPTIONS` routes; future CORS middleware must not make admin resources public. |
| Admin creation | `POST /api/v1/showcases` | Not approved | Current admin context required | Approved only for owner-scoped create boundary in `docs/decisions/admin-api-lifecycle.md`; storage and audit decisions still apply. |
| Admin clone/archive/restore actions | `POST /api/v1/showcases/{id}/clone`, `POST /api/v1/showcases/{id}/archive`, `POST /api/v1/showcases/{id}/restore` | Not approved | Current admin context required | Approved only for owner-scoped action boundaries in `docs/decisions/admin-api-lifecycle.md`; behavior and audit decisions still apply. |
| Admin replacement | `PUT` | Not approved | Current admin context required | Mutation permissions and audit requirements remain product decision required. |
| Admin partial updates | `PATCH /api/v1/showcases/{id}` | Not approved | Current admin context required | Approved only for owner-scoped draft patch boundary in `docs/decisions/admin-api-lifecycle.md`; patchable fields beyond the current title update remain product decision required. |
| Admin deletion | `DELETE` | Not approved | Current admin context required | Deletion permissions, recovery needs, and audit requirements remain product decision required. |

## Public Data And Identifiers

The only confirmed public runtime surface remains the existing `GET /health`
response. This record approves only the public identifier model for future
published snapshot reads; it does not register a public storefront route and
does not approve the public response-field set.

Future public reads use an opaque public showcase id, represented by the
`public_id` route parameter in the existing test helper path
`/api/v1/public/showcases/{public_id}` and by `id` on the current published
public config snapshot/response schemas. The id is a stable, non-semantic public
identifier assigned by the application for published snapshot lookup. It must
not be derived from, equal to, or reversible to an internal database id,
admin/user profile identifier, owner id, partner id, tenant/account id, email,
username, custom-domain value, or slug.

Public slugs, custom domains as identifiers, domain plus path routing, stable
aliases, and internal database IDs are not approved public identifier schemes in
the MVP. Future feature plans may use the opaque public id only after a separate
route decision approves the public method/path and a separate exposure decision
approves the response fields.

| Field class | Public exposure | Rationale |
| --- | --- | --- |
| Public showcase identifier | Approved MVP boundary: opaque public showcase id | Future public reads may use `public_id` in `/api/v1/public/showcases/{public_id}` and may expose the same opaque id as published snapshot `id` only after public route and response-field decisions are approved. |
| Internal database IDs | Not approved | Persistence identifiers must stay private unless a later decision approves a specific field and reason. |
| Owner/admin identifiers | Not approved | Admin emails, usernames, profile identifiers, and account owner identifiers must not be exposed publicly without explicit approval. |
| Tenant/account identifiers | Not approved | Tenant and account identifiers must not be exposed publicly before the isolation and discovery model is approved. |
| Public slug | Not approved | Human-readable or SEO slugs are blocked until collision handling, ownership, rename/redirect behavior, and public display rules are approved. |
| Domain names and custom domains | product decision required | Blocked as public identifiers until domain ownership verification, display rules, and response-field exposure are approved. |
| Domain plus path routing | Not approved | Blocked until custom-domain verification and path ownership semantics are approved. |
| Showcase content fields | product decision required | Blocked until approved public fields for title, description, theme, pages, assets, metadata, and publication state are defined. |
| Custom code metadata | product decision required | Blocked until custom-code permissions, review status, sanitization, and sandboxing decisions are approved. |
| Domain verification status | product decision required | Blocked until verification method and public/admin visibility are approved. |

## Persistence

The MVP storage boundary approves process-local in-memory admin showcase storage
for future MVP implementation. This boundary is non-durable, process-local, not
shared across workers, lost on process restart, and scoped to local, test, and
demo usage. It may support route and use-case wiring for MVP demonstration, but
it is not a substitute for production persistence and must not be used to claim
audit durability, publication durability, analytics retention, billing records,
custom-domain ownership durability, or multi-process consistency.

The current core storage interface is
`src/core/storages.py::AdminShowcaseStorage`, with `get_by_id()` and
`update_draft()` methods. Future in-memory implementation may add concrete
storage under `src/storages/` and DI provider wiring for that interface. This
record does not implement that storage, register routes, add runtime settings,
add dependencies, or create migrations.

Durable persistence remains `product decision required`. No feature plan may add
database, file, or external-service persistence; persistence runtime settings;
database dependencies; ORM models; migrations; or durable transaction behavior
until the backend, ownership model, migration strategy, runtime config boundary,
and transaction boundary are explicitly approved. Non-persistence runtime
configuration still requires the relevant feature decision and the project
config rules.

| Boundary | MVP decision | Required constraint |
| --- | --- | --- |
| Backend choice | Approved MVP boundary: process-local in-memory admin showcase storage | Storage is non-durable, test/demo scoped, lost on restart, not shared across workers, and not approved for production persistence. |
| Durable persistence backend | product decision required | Blocked until PostgreSQL, SQLite, file storage, an external service, or another durable backend is explicitly selected with ownership and migration rules. |
| Persistence runtime config | Not approved for in-memory MVP; product decision required for durable persistence | In-memory storage must not add database URLs, credentials, file paths, or persistence-specific settings. Durable settings may be added only when the backend needs and approves them. |
| Storage layer | Approved only for future in-memory concrete storage under `src/storages/` | Implementations must use the `storages` layer name; do not introduce `repositories` or `repos`. |
| Core storage interfaces | Existing interface acknowledged | `src/core/storages.py::AdminShowcaseStorage` already defines the admin showcase storage interface. Add or change core interfaces only when a use case requires them. |
| Ownership model | Core/use-case owned | Storage preserves owner/partner fields, but access decisions remain in core use cases using the current admin context; storage must not become the permission layer. |
| Migrations | Not approved for in-memory MVP; product decision required for durable persistence | Add `migrations` only when a database-backed model and migration policy are approved. |
| Transaction boundary | Project constraint approved | In-memory MVP storage has no database transaction. When a durable database exists, DI providers own the Unit of Work; storage and use case code must not call `session.commit()` or `session.begin()`. |
| Storage behavior | Project constraint approved | Storage methods perform persistence operations, avoid business logic, and return domain schemas rather than ORM models. |

## Domain Verification

The MVP domain verification method is `product decision required`. This record
does not choose DNS TXT records, CNAME validation, HTTP file validation, email
verification, provider API checks, manual review, or another ownership proof.
No custom-domain feature plan may implement verification clients, services,
storages, API routes, background jobs, or public verification fields until the
method and failure handling are approved.

| Verification question | MVP decision | Feature plan blocked |
| --- | --- | --- |
| Ownership proof method | product decision required | Custom domain feature plan. |
| Verification token format and storage | product decision required | Custom domain and persistence feature plans. |
| Retry, expiration, and failure handling | product decision required | Custom domain and publishing feature plans. |
| Activation after successful verification | product decision required | Public storefront and custom domain feature plans. |
| Public/admin visibility of verification status | product decision required | Public data, admin API, and custom domain feature plans. |

## Audit And Events

Audit/event durability is `product decision required`. This record does not
choose best-effort application logs, durable database audit records, outbox
events, external event streams, append-only storage, or another durability
mechanism. Future plans must not treat admin mutations, publishing, domain
verification, or custom-code changes as unaudited by default.

| Audited action class | Durability decision | Feature plan blocked |
| --- | --- | --- |
| Admin changes | product decision required | Admin API and persistence feature plans. |
| Showcase publishing changes | product decision required | Publishing, public storefront, and persistence feature plans. |
| Domain verification changes | product decision required | Custom domain, publishing, and persistence feature plans. |
| Custom code permission or content changes | product decision required | Custom code, admin API, and persistence feature plans. |
| Analytics or billing-relevant events | product decision required | Analytics, billing, and persistence feature plans. |

## Custom Code Permissions

Custom code permissions are `product decision required`. This record does not
approve storage, execution, rendering, preview, publication, or public exposure
for user-supplied CSS, HTML, JavaScript, external embeds, or server-side logic.
Future plans must not add rendering clients, sanitizer policies, sandbox
runtime, persistence fields, moderation workflow, or audit behavior until each
capability and required control is explicitly approved.

| Capability | MVP permission | Required controls before implementation |
| --- | --- | --- |
| Custom CSS | product decision required | Blocked until allowed selectors/properties, sanitization, storage, preview, publish review, and public rendering rules are approved. |
| Custom HTML | product decision required | Blocked until allowed tags/attributes, sanitizer behavior, link/media policy, storage, review, and public rendering rules are approved. |
| Custom JavaScript | product decision required | Blocked until execution sandboxing, CSP, network/API permissions, storage, review, audit, rollback, and public rendering rules are approved. |
| External embeds | product decision required | Blocked until provider allowlist, iframe sandboxing, CSP, privacy/data-sharing rules, review, and public rendering rules are approved. |
| Server-side custom code | product decision required | Blocked until server execution is explicitly allowed and isolation, resource limits, secrets/network restrictions, review, audit, and rollback controls are approved. |

## Blocking Decisions

- Product decision required: choose the external admin API auth-provider
  integration, refresh/session activation model, internal-admin override,
  production replacement criteria, and still-unresolved lifecycle behavior
  details before adding management behavior beyond the owner-scoped route
  boundary approved in `docs/decisions/admin-api-lifecycle.md`.
- Product decision required: choose public route methods and public data
  exposure rules before adding storefront routes or schemas. The identifier
  model is approved only as an opaque public showcase id and does not approve
  route registration by itself.
- Product decision required: choose the durable persistence backend, migration
  boundary, runtime config boundary, ownership model, and transaction behavior
  before adding database/file/external-service persistence, persistence-specific
  `src/config` settings, ORM models, database dependencies, or `migrations`.
  Future MVP implementation may add only the approved process-local in-memory
  `src/storages` implementation for `AdminShowcaseStorage`.
- Product decision required: choose the domain verification method before adding
  custom-domain clients, services, storages, or API routes.
- Product decision required: choose audit/event durability requirements before
  adding admin mutations, publishing actions, domain verification changes, or
  custom-code changes.
- Product decision required: choose custom code permissions and required controls
  before rendering or storing user-supplied CSS, HTML, JavaScript, embeds, or
  server-side logic.

## Blocked Feature Plans

- Admin API feature plans beyond the owner-scoped showcase route boundary must
  wait for the final auth provider and any still-unresolved behavior,
  persistence, audit, and field-exposure decisions.
- Public storefront feature plans may use the approved opaque public showcase id,
  but must still wait for public route and field-exposure decisions before
  registering storefront endpoints.
- Durable persistence feature plans must wait for backend, migration, config,
  ownership, and transaction-boundary decisions. MVP admin showcase feature plans
  may use the approved process-local in-memory storage boundary only where
  non-durable test/demo behavior is acceptable.
- Custom domain feature plans must wait for verification-method and durability
  decisions.
- Analytics and billing feature plans must wait for explicit MVP scope and data
  exposure decisions.
- Custom code feature plans must wait for permission, sanitization, sandboxing,
  and review decisions.
