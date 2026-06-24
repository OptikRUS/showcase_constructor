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
| Showcase publishing | Published snapshot response-field boundary and in-memory audit/event boundary approved; publication workflow product decision required | Future public exposure is approved only for the published snapshot field groups listed below. Publication states, publish/unpublish behavior, and rollback remain blocked until focused decisions approve them; future publishing mutations must use the audit/event boundary below. |
| Custom domains | DNS TXT ownership-proof boundary approved; routing and production activation behavior product decision required | Future MVP planning may use the DNS TXT verification method defined below. Custom-domain routing, activation after verification, public route exposure, and public status visibility remain blocked until focused decisions approve them; future verification changes must use the audit/event boundary below. |
| Analytics | product decision required | Blocked until event collection, retention, and public/admin visibility are approved. |
| Billing | product decision required | Blocked until paid features, account ownership, and provider integration are approved. |
| Admin API | MVP JWT bearer adapter plus approved admin showcase route and in-memory audit/event boundaries | `docs/decisions/admin-api-lifecycle.md` approves protected owner-scoped create, list own, get own, patch draft, clone, archive, and restore route boundaries; storage and lifecycle behavior still require their focused decisions, and approved mutations must use the audit/event boundary below. |
| Public storefront | Opaque public showcase id and published snapshot response-field boundary approved; route methods product decision required | Future public reads may address a published snapshot by opaque public showcase id and may return only the approved published snapshot field groups below. Public route registration and methods remain blocked until a focused public-route decision approves them. |
| Persistence | Approved in-memory MVP storage boundary; durable persistence product decision required | Future MVP implementation may add only process-local, non-durable `src/storages` storage for admin showcase flows and DNS TXT domain verification state. Database/file/external persistence, runtime config, migrations, and durability claims remain blocked until a durable backend decision is approved. |
| Custom code | product decision required | Blocked until allowed code categories, sanitization, sandboxing, and review rules are approved; future permission or content changes must use the audit/event boundary below. |

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
`unarchive` alias blocked. Storage and lifecycle behavior remain governed by
their focused decisions before implementation may go live. Approved admin
mutations must emit process-local in-memory audit records under the audit/event
boundary below; durable audit remains blocked.
Public identifiers use the opaque public showcase id boundary below; slugs and
custom-domain identifiers remain blocked.

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
| Admin creation | `POST /api/v1/showcases` | Not approved | Current admin context required | Approved only for owner-scoped create boundary in `docs/decisions/admin-api-lifecycle.md`; storage, lifecycle behavior, and the audit/event boundary still apply. |
| Admin clone/archive/restore actions | `POST /api/v1/showcases/{id}/clone`, `POST /api/v1/showcases/{id}/archive`, `POST /api/v1/showcases/{id}/restore` | Not approved | Current admin context required | Approved only for owner-scoped action boundaries in `docs/decisions/admin-api-lifecycle.md`; behavior and the audit/event boundary still apply. |
| Admin replacement | `PUT` | Not approved | Current admin context required | Mutation permissions and behavior remain product decision required; any later approval must use the audit/event boundary below. |
| Admin partial updates | `PATCH /api/v1/showcases/{id}` | Not approved | Current admin context required | Approved only for owner-scoped draft patch boundary in `docs/decisions/admin-api-lifecycle.md`; patchable fields beyond the current title update remain product decision required. |
| Admin deletion | `DELETE` | Not approved | Current admin context required | Deletion permissions, recovery needs, and behavior remain product decision required; any later approval must use the audit/event boundary below. |

## Public Data And Identifiers

The only confirmed public runtime surface remains the existing `GET /health`
response. This record approves the public identifier model and response-field
boundary for future published snapshot reads; it does not register a public
storefront route, approve public route methods, or implement a public endpoint.

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
the MVP. Future feature plans may use the opaque public id and approved field
groups below only after a separate public-route decision approves the method and
path.

Approved public fields must be read from the published snapshot shape currently
represented by `src/core/public_config/schemas.py::PublishedPublicConfigSnapshot`
and serialized by `src/api/public_config/schemas.py::PublicConfigResponse`.
Draft data, admin-only data, and storage-private data must not be copied into
that public payload.

| Field class | Public exposure | Rationale |
| --- | --- | --- |
| Public showcase identifier | Approved MVP boundary: opaque public showcase id | Future public reads may use `public_id` in `/api/v1/public/showcases/{public_id}` and may expose the same opaque id as published snapshot `id` only after a public route method/path is approved. |
| Published snapshot `id` | Approved public data | Exposes only the opaque public showcase id for the published snapshot; it is not an internal storage id. |
| Published snapshot `affiliateId` | Approved public data | Existing candidate response exposes the affiliate-facing public value needed by the widget/showcase runtime. It must not be an owner, tenant, account, admin, or internal storage identifier. |
| Published snapshot `type` | Approved public data | Existing candidate response exposes the public config type, such as widget or showcase rendering mode. |
| Published snapshot `settings` | Approved public data | Existing candidate response exposes public presentation and routing settings only, such as colors, text, images, placement, alignment, and sort settings. Private service settings, credentials, moderation state, and draft-only settings remain blocked. |
| Published snapshot `platform.id` | Approved public data | Existing candidate response exposes the public platform identifier needed by the client runtime, such as `widgetmarket`. It must not expose tenant/account ownership. |
| Published snapshot URL params tools | Approved public data for `constantUrlParamsTool` and `transferredUrlParamsTool` | Existing candidate response exposes only enabled flags and public key/value mappings required by outbound URL behavior. Secrets, account ids, admin identifiers, and private tracking configuration remain blocked. |
| Published snapshot `metricsTool` | Approved public data | Existing candidate response exposes only enabled flags and public metric handles needed by the client runtime. Private analytics credentials, admin-only stats, and billing data remain blocked. |
| Published snapshot `blocks` | Approved public data | Existing candidate response exposes public block type, title, and nested `offers` content for published showcase rendering. Draft block ids, internal block ids, moderation state, and private layout metadata remain blocked. |
| Published snapshot `widgetInfo` | Approved public data | Existing candidate response exposes public widget runtime metadata, nested `offers`, and `triggerGroups`. Private widget settings, admin preview state, and unpublished draft metadata remain blocked. |
| Published snapshot `offers` | Approved public data | Existing candidate response exposes public offer id, categories, logo URLs, display names, target URL, and visible field key/value data under `blocks` or `widgetInfo`. Internal offer ids, source-system ids, private payout/billing fields, and hidden fields remain blocked. |
| Published snapshot `triggerGroups` | Approved public data | Existing candidate response exposes public trigger type and delay values needed by widget runtime behavior. Internal rule ids, targeting segments, and unpublished experiment data remain blocked. |
| Published snapshot `is_need_to_send_offers_display_and_positions` | Approved public data | Existing candidate response exposes this runtime compatibility flag as part of the published public config contract. It must not imply exposure of private analytics or admin stats. |
| Internal database IDs | Not approved | Persistence identifiers must stay private unless a later decision approves a specific field and reason. |
| Owner/admin identifiers | Not approved | Admin emails, usernames, profile identifiers, and account owner identifiers must not be exposed publicly without explicit approval. |
| Tenant/account identifiers | Not approved | Tenant and account identifiers must not be exposed publicly before the isolation and discovery model is approved. |
| Draft version ids and draft data | Not approved | Public responses may use only the published snapshot. Draft version ids, dirty state, unpublished draft fields, and admin preview data remain private. |
| Private stats and service settings | Not approved | Private analytics, service credentials, payout/billing data, moderation state, and operational settings are not public snapshot data. |
| Internal nested offer/block ids | Not approved | Public `offers` and `blocks` may include only approved public ids and display fields; internal offer ids, block ids, source ids, and storage ids remain private. |
| Public slug | Not approved | Human-readable or SEO slugs are blocked until collision handling, ownership, rename/redirect behavior, and public display rules are approved. |
| Domain names and custom domains | Not approved as public identifiers | DNS TXT verification is approved below only as an ownership-proof method. Custom domains, domain plus path routing, display rules, and response-field exposure remain blocked as public identifier schemes until a focused routing/public-exposure decision approves them. |
| Domain plus path routing | Not approved | DNS TXT verification does not approve Host-based routing, path ownership semantics, or public renderer domain lookup behavior. |
| Showcase content fields outside the published public config snapshot | product decision required | Future title, description, theme, page, asset, SEO metadata, and publication-state fields remain blocked unless they are added to an approved published snapshot contract by a later decision. |
| Custom code metadata | product decision required | Blocked until custom-code permissions, review status, sanitization, and sandboxing decisions are approved. |
| Domain verification status | Not approved for public exposure; protected owner-admin visibility may be approved by a later route plan | DNS TXT verification status may be returned only through future authenticated owner-scoped admin domain management routes after those routes are approved. Public storefront responses must not expose verification status. |

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
storage under `src/storages/` and DI provider wiring for that interface. A
future DNS TXT domain verification plan may add a core-owned storage interface
and process-local in-memory `src/storages/` implementation only for verification
tokens and statuses. This record does not implement that storage, register
routes, add runtime settings, add dependencies, or create migrations.

Durable persistence remains `product decision required`. No feature plan may add
database, file, or external-service persistence; persistence runtime settings;
database dependencies; ORM models; migrations; or durable transaction behavior
until the backend, ownership model, migration strategy, runtime config boundary,
and transaction boundary are explicitly approved. Non-persistence runtime
configuration still requires the relevant feature decision and the project
config rules.

| Boundary | MVP decision | Required constraint |
| --- | --- | --- |
| Backend choice | Approved MVP boundary: process-local in-memory admin showcase storage and DNS TXT domain verification state | Storage is non-durable, test/demo scoped, lost on restart, not shared across workers, and not approved for production persistence. |
| Durable persistence backend | product decision required | Blocked until PostgreSQL, SQLite, file storage, an external service, or another durable backend is explicitly selected with ownership and migration rules. |
| Persistence runtime config | Not approved for in-memory MVP; product decision required for durable persistence | In-memory storage must not add database URLs, credentials, file paths, or persistence-specific settings. Durable settings may be added only when the backend needs and approves them. |
| Storage layer | Approved only for future in-memory concrete storage under `src/storages/` | Implementations must use the `storages` layer name; do not introduce `repositories` or `repos`. |
| Core storage interfaces | Existing interface acknowledged | `src/core/storages.py::AdminShowcaseStorage` already defines the admin showcase storage interface. Add or change core interfaces only when a use case requires them. |
| Ownership model | Core/use-case owned | Storage preserves owner/partner fields, but access decisions remain in core use cases using the current admin context; storage must not become the permission layer. |
| Migrations | Not approved for in-memory MVP; product decision required for durable persistence | Add `migrations` only when a database-backed model and migration policy are approved. |
| Transaction boundary | Project constraint approved | In-memory MVP storage has no database transaction. When a durable database exists, DI providers own the Unit of Work; storage and use case code must not call `session.commit()` or `session.begin()`. |
| Storage behavior | Project constraint approved | Storage methods perform persistence operations, avoid business logic, and return domain schemas rather than ORM models. |

## Domain Verification

The MVP domain verification method is DNS TXT ownership proof. A future
custom-domain implementation may generate an opaque verification token, show the
owner DNS instructions for a TXT record, check that TXT record for the requested
host, and update process-local in-memory verification state for local/test/demo
usage. This boundary does not approve CNAME validation, HTTP file validation,
email verification, provider API checks, manual review, custom-domain routing,
or production publication on a custom domain.

The verification token must be generated by the application as an opaque,
unguessable value. It must not contain or derive from internal storage ids,
owner/admin identifiers, partner ids, tenant/account ids, emails, usernames,
profile identifiers, custom-code metadata, or public slugs. Token and status
storage may use only the approved process-local, non-durable in-memory storage
boundary; durable domain storage, file storage, external-provider state, runtime
DNS provider settings, and migrations remain blocked.

| Verification question | MVP decision | Feature plan boundary |
| --- | --- | --- |
| Ownership proof method | Approved MVP boundary: DNS TXT record containing an opaque application-generated token for the requested host | Future custom-domain verification planning may implement TXT lookup/check behavior only; CNAME, HTTP file, email, provider API, and manual verification remain blocked. |
| Verification token format and storage | Approved MVP boundary: opaque unguessable token stored only in process-local in-memory domain verification state | No durable persistence, config, migrations, external storage, or token values derived from private identifiers are approved. |
| Retry, expiration, and failure handling | product decision required beyond safe recheck attempts | A future implementation may support explicit owner-triggered rechecks against the current TXT record. Automatic retry schedules, token expiration, background jobs, lockouts, and failure-state transition policy remain blocked until a focused custom-domain plan approves them. |
| Activation after successful verification | product decision required | Verification may establish ownership state only. Custom-domain routing, production activation, Host-based public rendering, domain detachment, and publication behavior remain blocked for public storefront and custom-domain feature plans. |
| Public/admin visibility of verification status | Public visibility not approved; authenticated owner-admin visibility product decision required by route | Verification status must not appear in public storefront responses. A future protected owner-scoped admin domain route may request approval to return status values such as pending, verified, failed, active, or disabled. |

## Audit And Events

The MVP audit/event boundary approves process-local in-memory audit records for
future test/demo implementation. This boundary depends on the in-memory storage
decision above: audit records are non-durable, retained only for the current
process lifetime, lost on restart, not shared across workers, and not suitable
for production compliance, billing, analytics, or incident reconstruction.

Every approved audited mutation must write an audit record in the same
request/use-case flow after the owner and permission checks succeed. Records may
be exposed only to authenticated admin tooling approved by a later feature plan;
this decision does not approve public audit data, public verification status, or
private actor identifiers in storefront responses.

Durable database audit records, transactional outbox events, external event
streams, append-only storage, background delivery, cross-process ordering,
retention beyond process lifetime, and production audit guarantees remain
`product decision required`. If a later plan selects durable persistence, it
must revisit audit durability instead of carrying this non-durable MVP boundary
into production.

| Audited action class | Durability decision | Feature plan boundary |
| --- | --- | --- |
| Admin create showcase | Approved MVP boundary: process-local in-memory audit record | Future owner-scoped `POST /api/v1/showcases` implementation must record actor context, owned showcase id, action type, timestamp, and allowed response metadata. Durable audit remains blocked. |
| Admin patch draft showcase | Approved MVP boundary: process-local in-memory audit record | Future owner-scoped `PATCH /api/v1/showcases/{id}` implementation must record actor context, owned showcase id, action type, timestamp, and changed field names or safe metadata. Draft content diffs, private settings, and durable audit remain blocked. |
| Admin clone showcase | Approved MVP boundary: process-local in-memory audit record | Future owner-scoped clone implementation must record actor context, source showcase id, cloned showcase id, action type, timestamp, and safe metadata. Copy semantics and durable audit remain blocked by their own decisions. |
| Admin archive showcase | Approved MVP boundary: process-local in-memory audit record | Future owner-scoped archive implementation must record actor context, owned showcase id, action type, timestamp, and safe archive metadata. Archive behavior and durable audit remain blocked by their own decisions. |
| Admin restore showcase | Approved MVP boundary: process-local in-memory audit record | Future owner-scoped restore implementation must record actor context, owned showcase id, action type, timestamp, and safe restore metadata. Restore behavior and durable audit remain blocked by their own decisions. |
| Admin unarchive alias | Blocked | The admin lifecycle boundary selects `POST /api/v1/showcases/{id}/restore`; no separate unarchive audit event is approved unless the alias is later approved. |
| Showcase publishing changes | Approved MVP boundary: process-local in-memory audit record | If a later publishing decision approves publish, unpublish, rollback, or republish behavior, each mutation must record actor context, showcase id, action type, timestamp, and safe snapshot metadata. Publishing behavior and durable audit remain blocked until separately approved. |
| Domain verification changes | Approved MVP boundary: process-local in-memory audit record | Future DNS TXT verification requests, owner-triggered rechecks, and safe status updates must record actor context when present, domain identifier, action type, timestamp, and safe verification metadata. Activation, expiration, automatic retry policy, public/admin status visibility, and durable audit remain blocked. |
| Custom code permission or content changes | Approved MVP boundary: process-local in-memory audit record | If a later custom-code decision approves CSS, HTML, JavaScript, embeds, or server-side code permissions, each permission or content change must record actor context, showcase id, capability, action type, timestamp, and safe metadata. Code content, secrets, and durable audit remain blocked. |
| Analytics or billing-relevant events | product decision required | Analytics, billing, event collection, retention, and public/admin visibility remain blocked; the non-durable audit boundary must not be reused as analytics or billing event storage. |

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
- Product decision required: choose public route methods before adding storefront
  routes. The identifier model is approved only as an opaque public showcase id,
  and the public response-field boundary is approved only for the published
  snapshot groups listed above; neither decision approves route registration by
  itself.
- Product decision required: choose the durable persistence backend, migration
  boundary, runtime config boundary, ownership model, and transaction behavior
  before adding database/file/external-service persistence, persistence-specific
  `src/config` settings, ORM models, database dependencies, or `migrations`.
  Future MVP implementation may add only the approved process-local in-memory
  `src/storages` implementation for `AdminShowcaseStorage`.
- Product decision required: choose custom-domain routing, activation after
  verification, public/admin status visibility routes, automatic retry,
  expiration, failure-state transition policy, and durable domain storage before
  adding behavior beyond the approved DNS TXT ownership proof and process-local
  verification state.
- Approved MVP boundary: future test/demo admin mutations, publishing actions,
  domain verification changes, and custom-code changes may use process-local
  in-memory audit records as defined above. Product decision required: choose
  durable database audit records, outbox events, external event streams,
  retention, delivery, and production audit guarantees before claiming durable
  audit/event behavior.
- Product decision required: choose custom code permissions and required controls
  before rendering or storing user-supplied CSS, HTML, JavaScript, embeds, or
  server-side logic.

## Blocked Feature Plans

- Admin API feature plans beyond the owner-scoped showcase route boundary must
  wait for the final auth provider and any still-unresolved behavior,
  persistence, and public route method/path decisions; approved test/demo
  mutations must use the process-local in-memory audit boundary above.
- Public storefront feature plans may use the approved opaque public showcase id
  and approved published snapshot response-field boundary, but must still wait
  for a public route method/path decision before registering storefront
  endpoints.
- Durable persistence feature plans must wait for backend, migration, config,
  ownership, and transaction-boundary decisions. MVP admin showcase feature plans
  may use the approved process-local in-memory storage boundary only where
  non-durable test/demo behavior is acceptable.
- Custom domain feature plans may use the approved DNS TXT ownership-proof
  method and process-local verification state for local/test/demo flows, but
  must wait for routing, activation, status-visibility, retry/expiration/failure
  policy, and durable storage decisions before production custom-domain
  behavior; approved verification changes must use the process-local in-memory
  audit boundary above until durable audit is separately approved.
- Analytics and billing feature plans must wait for explicit MVP scope and data
  exposure decisions.
- Custom code feature plans must wait for permission, sanitization, sandboxing,
  and review decisions; approved permission or content changes must use the
  process-local in-memory audit boundary above until durable audit is separately
  approved.
