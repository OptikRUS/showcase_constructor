# MVP Boundaries

## Scope

This record is the current decision boundary for the showcase constructor MVP. It
does not approve business implementation, new routes, persistence, runtime
configuration, migrations, or custom rendering behavior.

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
  billing, admin API, or public storefront behavior as approved MVP features.
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
| Admin API | product decision required | Blocked until the admin auth model and method permissions are approved. |
| Public storefront | product decision required | Blocked until public identifiers, routes, and response fields are approved. |
| Persistence | product decision required | Blocked until backend, migration, and transaction boundaries are approved. |
| Custom code | product decision required | Blocked until allowed code categories, sanitization, sandboxing, and review rules are approved. |

## Admin API Auth

The admin API auth model is `product decision required`. This record does not
choose token auth, session auth, API keys, mTLS, OAuth, internal network access,
or another protection model. No admin API feature plan may implement management
routes until the model and per-method permissions are approved.

The only confirmed public runtime route remains `GET /health`. No future admin
`GET`, `HEAD`, `OPTIONS`, `POST`, `PUT`, `PATCH`, or `DELETE` route is public
unless a later decision record explicitly approves that method, path, and
rationale.

| Surface | Method class | Public access | Required auth | Status |
| --- | --- | --- | --- | --- |
| Admin management reads | `GET` | product decision required | product decision required | Blocked until readable resources and permissions are approved. |
| Admin read metadata | `HEAD` | product decision required | product decision required | Blocked until parity with admin `GET` routes is approved. |
| Admin preflight/discovery | `OPTIONS` | product decision required | product decision required | Blocked until CORS/preflight and discovery behavior are approved. |
| Admin creation | `POST` | Not approved | product decision required | Blocked until mutation permissions and audit requirements are approved. |
| Admin replacement | `PUT` | Not approved | product decision required | Blocked until mutation permissions and audit requirements are approved. |
| Admin partial updates | `PATCH` | Not approved | product decision required | Blocked until mutation permissions and audit requirements are approved. |
| Admin deletion | `DELETE` | Not approved | product decision required | Blocked until deletion permissions, recovery needs, and audit requirements are approved. |

## Public Data And Identifiers

The only confirmed public data surface remains the existing `GET /health`
response. No showcase, owner, domain, theme, page, asset, custom-code, analytics,
billing, or verification-status field is approved for public storefront exposure
by this record.

No public identifier scheme is selected yet. Future feature plans must not
assume public slugs, opaque public IDs, custom domains, stable aliases, or
internal database IDs until the identifier model is explicitly approved.

| Field class | Public exposure | Rationale |
| --- | --- | --- |
| Public showcase identifier | product decision required | Blocked until the product chooses public slugs, opaque IDs, custom domains, another identifier scheme, or no public identifier. |
| Internal database IDs | Not approved | Persistence identifiers must stay private unless a later decision approves a specific field and reason. |
| Owner/admin identifiers | Not approved | Admin emails, usernames, profile identifiers, and account owner identifiers must not be exposed publicly without explicit approval. |
| Tenant/account identifiers | Not approved | Tenant and account identifiers must not be exposed publicly before the isolation and discovery model is approved. |
| Domain names and custom domains | product decision required | Blocked until domain ownership verification, display rules, and response-field exposure are approved. |
| Showcase content fields | product decision required | Blocked until approved public fields for title, description, theme, pages, assets, metadata, and publication state are defined. |
| Custom code metadata | product decision required | Blocked until custom-code permissions, review status, sanitization, and sandboxing decisions are approved. |
| Domain verification status | product decision required | Blocked until verification method and public/admin visibility are approved. |

## Persistence

The MVP persistence backend is `product decision required`. This record does not
choose PostgreSQL, SQLite, in-memory storage, file storage, an external service,
or any other backend. No feature plan may add persistence runtime settings,
storage implementations, storage interfaces, migrations, or database
dependencies until the backend and migration boundary are explicitly approved.

Future plans may introduce `src/config`, `src/storages`, `src/core/storages.py`,
and `migrations` only after the persistence backend, ownership model, migration
strategy, and transaction boundary are approved. Until then, any persistence
implementation remains blocked.

| Boundary | MVP decision | Required constraint |
| --- | --- | --- |
| Backend choice | product decision required | Blocked until the MVP chooses durable database storage, in-memory-only behavior, or another explicit backend. |
| Runtime config | product decision required | `src/config` may be added only when runtime settings such as database URLs, credentials, or paths are needed and approved. |
| Storage layer | product decision required | Persistent implementations must live under `src/storages`; do not introduce `repositories` or `repos`. |
| Core storage interfaces | product decision required | Add `src/core/storages.py` only when a use case needs an interface owned by `src/core`. |
| Migrations | product decision required | Add `migrations` only when a database-backed model and migration policy are approved. |
| Transaction boundary | Project constraint approved | DI providers own the Unit of Work; storage and use case code must not call `session.commit()` or `session.begin()`. |
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

## Blocking Decisions

- Product decision required: choose the admin API auth model and per-method
  permissions before adding management routes.
- Product decision required: choose the public identifier model and public data
  exposure rules before adding storefront routes or schemas.
- Product decision required: choose the persistence backend and migration
  boundary before adding `src/config`, `src/storages`, `src/core/storages.py`, or
  `migrations`.
- Product decision required: choose the domain verification method before adding
  custom-domain clients, services, storages, or API routes.
- Product decision required: choose audit/event durability requirements before
  adding admin mutations, publishing actions, domain verification changes, or
  custom-code changes.
- Product decision required: choose custom code permissions and required controls
  before rendering or storing user-supplied CSS, HTML, JavaScript, embeds, or
  server-side logic.

## Blocked Feature Plans

- Admin API feature plans must wait for the admin auth model, method matrix, and
  protected/public route decisions.
- Public storefront feature plans must wait for public route, field exposure, and
  identifier decisions.
- Persistence feature plans must wait for backend, migration, config, and
  transaction-boundary decisions.
- Custom domain feature plans must wait for verification-method and durability
  decisions.
- Analytics and billing feature plans must wait for explicit MVP scope and data
  exposure decisions.
- Custom code feature plans must wait for permission, sanitization, sandboxing,
  and review decisions.
