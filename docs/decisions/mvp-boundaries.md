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
