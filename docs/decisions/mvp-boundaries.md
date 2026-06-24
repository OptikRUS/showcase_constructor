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

## Blocking Decisions

- Product decision required: choose the admin API auth model and per-method
  permissions before adding management routes.
- Product decision required: choose the public identifier model before adding
  storefront routes or schemas.
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
