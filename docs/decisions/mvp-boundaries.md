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
| Admin API | MVP JWT bearer adapter plus approved admin showcase route, in-memory storage, and in-memory audit/event boundaries | `docs/decisions/admin-api-lifecycle.md` approves protected owner-scoped create, list own, get own, patch draft, clone, archive, and restore route boundaries; test/demo storage must use the in-memory boundary below, lifecycle behavior still requires focused decisions, and approved mutations must use the audit/event boundary below. |
| Public storefront | Opaque public showcase id and published snapshot response-field boundary approved; route methods product decision required | Future public reads may address a published snapshot by opaque public showcase id and may return only the approved published snapshot field groups below. Public route registration and methods remain blocked until a focused public-route decision approves them. |
| Persistence | Approved in-memory MVP storage boundary; durable persistence product decision required | Future MVP implementation may add only process-local, non-durable `src/storages` storage for admin showcase flows and DNS TXT domain verification state. Database/file/external persistence, runtime config, migrations, and durability claims remain blocked until a durable backend decision is approved. |
| Custom code | Approved MVP boundary: no user-supplied custom code | Custom CSS, HTML, JavaScript, external embeds, and server-side custom code are forbidden in MVP. Future post-MVP permission or content changes require explicit controls and must use the audit/event boundary below. |

## Admin API Auth

### MVP JWT bearer adapter

This MVP boundary uses a `fastapi-jwt` bearer token adapter to establish the
owner-aware admin boundary. The JWT subject must contain `user_id` and
`partner_id`; missing, invalid, or blank values are unauthenticated.

The JWT adapter may protect `GET /api/v1/admin/auth/context` and future admin
showcase use cases that consume the current admin context. It does not approve
public admin data exposure and does not approve an internal-admin cross-partner
override.

The trust boundary for all approved admin routes is the already-validated
`AdminActorContext` resolved by the API auth layer. Owner, partner, actor,
public-id, status, and lifecycle fields from request bodies, query parameters, or
path parameters must not be trusted as authorization inputs. Endpoints pass the
current context and route/body payload to exactly one use case; use cases perform
owner/status checks before storage mutation or audit append.

Foreign-resource semantics are approved for protected admin routes: unauthenticated
requests fail as `401`, authenticated requests for a resource owned by a different
`partner_id` fail as `403`, and missing resources fail as `404`. List-own
responses omit foreign resources. Failed `401`, `403`, and `404` requests must
not mutate storage and must not append audit records.

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

Public ids are generated by the application from a cryptographically secure
random source using at least 128 bits of entropy, such as `secrets.token_urlsafe`.
Generation must happen inside the storage mutation that creates the public-id
binding, and uniqueness must be checked against current in-memory state under the
same lock as the write. A collision retries generation; repeated collision
failure aborts the create/clone operation without exposing a partial resource.

Public ids are stable for the resource lifetime. Rotation, aliases, redirects,
human-readable slugs, and custom-domain ids are not approved in MVP. A deleted or
archived resource's public id must not be reused during the current process
lifetime; no reuse guarantee is claimed after process restart because the
approved storage boundary is non-durable. Draft, unpublished, archived, and
missing resources must not resolve through public storefront reads; route-level
status behavior still requires the public-route decision below.

### Public Storefront Route Status

No public storefront route is approved for registration by this record. The
candidate `GET /api/v1/public/showcases/{public_id}` route, any explicit `HEAD`
route, and any app-defined `OPTIONS` route remain blocked until a focused public
route decision approves method/path exposure, cache behavior, and error
semantics. Until then, the approved public-id and published-snapshot field
boundaries are usable only as input to a later route plan, not as route
registration approval.

The blocked follow-up public-route decision must either approve or reject these
MVP invariants before implementation: `GET` returns only an existing published
snapshot addressed by opaque public id; missing, draft, unpublished, and archived
resources return `404`; `HEAD` is either not app-defined or mirrors the approved
`GET` authorization and existence semantics without a body; `OPTIONS`, if
introduced through middleware, must not expose private resource existence; public
reads do not mutate counters, analytics, audit records, or storage state unless a
separate counter/analytics decision approves that mutation path.

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
| Custom code metadata | Not approved | MVP forbids user-supplied custom code, so public responses must not expose custom-code metadata, review state, sanitizer state, sandbox settings, or custom-code publication state. |
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

In-memory mutable state is application/process scoped, not request scoped. A
request-scoped storage adapter may be used to match DI conventions, but it must
reference a single app-scoped state owner for the process. The mutable state
owner is the concrete `src/storages/` in-memory state object; API endpoints, use
cases, tests, and helpers must not mutate its dictionaries/lists directly.

All compound read/write operations on in-memory showcase, public-id, domain
verification, and audit state require concurrency protection with an
implementation-local lock, such as `asyncio.Lock`. Storage methods must not
return live mutable references: stored inputs are copied or converted into
domain schemas, and returned domain objects are copies/snapshots isolated from
future mutations.

Reset lifecycle is limited to process start, app/container construction, and
test fixture teardown or new-app creation. No admin or public runtime reset route
is approved. Local/demo operators must treat restart as data loss, not as a
persistence recovery operation.

Owner and status mutations must be atomic within the in-memory lock. Create,
update draft, clone, archive, restore, public-id assignment, domain token/status
updates, and audit append must validate owner/status preconditions and commit all
state changes as one process-local critical section, or leave state unchanged on
failure. Split read-then-write flows outside the lock are not approved for these
mutations.

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
| Application/request scope | Approved MVP boundary: app/process-scoped mutable state with optional request-scoped adapter | Mutable state has one owner per app process. Request-scoped objects must reference that owner rather than creating isolated per-request stores. |
| Concurrency protection | Approved MVP boundary: lock-protected process-local critical sections | All owner/status/public-id/domain/audit mutations must run under the in-memory state lock and must be all-or-nothing within that process. |
| Copy and isolation | Approved MVP boundary: no live mutable references escape storage | Store copies/snapshots and return domain objects that cannot mutate the backing store by reference. |
| Reset lifecycle | Approved MVP boundary: process/app/test lifecycle only | Restart, app/container reconstruction, and test teardown may reset state. Runtime reset endpoints are not approved. |
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

The approved TXT record name is `_showcase-constructor.<requested-host>`, where
`<requested-host>` is the exact normalized host being verified. The approved TXT
value format is `showcase-constructor-verification=<token>`. The token is
generated with a cryptographically secure random source using at least 192 bits
of entropy, such as `secrets.token_urlsafe(32)`.

Token lifetime is the current process lifetime unless the owner explicitly
regenerates the token. There is no durable token recovery after restart and no
automatic expiration, background refresh, or scheduled retry in MVP. Regeneration
invalidates the previous token for that in-memory state.

Verification checks are owner-triggered revalidation attempts against the current
TXT record. A single recheck may perform at most two resolver attempts with a
per-attempt timeout of two seconds. Timeout, NXDOMAIN, resolver error, or missing
matching token leaves the domain unverified or moves an already verified
process-local state to ownership-lost/pending recheck; it must not activate or
route traffic. DNS resolver library/package selection remains an implementation
plan concern and must follow dependency rules if a new dependency is required.

DNS verification proves only control of the requested host at the time of the
latest successful recheck. It does not approve custom-domain route activation,
public storefront host routing, domain detachment behavior, production
publication, public status exposure, or durable ownership claims.

| Verification question | MVP decision | Feature plan boundary |
| --- | --- | --- |
| Ownership proof method | Approved MVP boundary: DNS TXT record at `_showcase-constructor.<requested-host>` containing `showcase-constructor-verification=<token>` | Future custom-domain verification planning may implement TXT lookup/check behavior only; CNAME, HTTP file, email, provider API, and manual verification remain blocked. |
| Verification token format and storage | Approved MVP boundary: opaque token with at least 192 bits of randomness stored only in process-local in-memory domain verification state | No durable persistence, config, migrations, external storage, or token values derived from private identifiers are approved. |
| Retry, expiration, and failure handling | Approved MVP boundary for owner-triggered recheck only | Each recheck may use at most two resolver attempts with two-second per-attempt timeout. No automatic retry schedule, durable lockout, background job, or automatic expiration is approved. |
| Ownership loss and revalidation | Approved MVP boundary: latest recheck controls process-local verification state | Failed recheck or missing token must not activate routing and may mark the in-memory verification as pending/lost. Durable ownership history remains blocked. |
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

Audit append is mandatory for every approved audited mutation, not best-effort.
For process-local in-memory MVP behavior, mutation and audit append must share
one lock-protected critical section. If the audit record cannot be appended, the
business mutation must not become visible and the request must fail without a
partial state change. This all-or-nothing guarantee is process-local only and
does not claim database transactionality or cross-process atomicity.

Audit actor attribution records the authenticated `user_id` and `partner_id`
from `AdminActorContext` for admin-triggered mutations. Domain verification
actions triggered by an owner-admin use the same actor context; system or
background actors are not approved in MVP. Audit metadata must not include
secrets, custom-code contents, private service settings, or full draft/published
snapshot payloads.

Audit ordering is append order inside the current process and lock. No
cross-process order, exactly-once delivery, idempotency key, or duplicate
suppression guarantee is approved. If a client retries a completed mutation, a
later implementation must either append a second audit record or first add an
idempotency decision.

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
| Custom code permission or content changes | Blocked by the current custom-code permission boundary; future approved changes must use process-local in-memory audit records | MVP forbids CSS, HTML, JavaScript, embeds, and server-side custom code changes. If a later decision approves any category, each permission or content change must record actor context, showcase id, capability, action type, timestamp, and safe metadata. Code content, secrets, and durable audit remain blocked. |
| Analytics or billing-relevant events | product decision required | Analytics, billing, event collection, retention, and public/admin visibility remain blocked; the non-durable audit boundary must not be reused as analytics or billing event storage. |

## Custom Code Permissions

The MVP custom-code permission boundary is an explicit prohibition: no
user-supplied custom CSS, custom HTML, custom JavaScript, external embeds, or
server-side custom code may be stored, executed, rendered, previewed, published,
or exposed publicly in MVP. This is an approved MVP boundary, not an unresolved
permission question.

Future plans may rely on the absence of custom-code behavior for MVP work. They
must not add rendering clients, sanitizer policies, sandbox runtime, persistence
fields, moderation workflow, preview/public rendering paths, publication state,
rollback state, or custom-code audit writes unless a later decision approves a
specific category and every required control for that category. Any later
approved custom-code permission or content change must use the process-local
in-memory audit/event boundary above until durable audit is separately approved.

MVP request schemas, storage schemas, published snapshots, admin responses, and
public responses must not include custom-code fields. If a future endpoint or
import path receives custom CSS, HTML, JavaScript, embed markup, server-side code,
or custom-code metadata before a later approval, it must reject the payload or
drop the field before persistence according to that endpoint's explicit
validation contract; it must never store, echo, preview, render, execute, publish,
or audit raw code content in MVP.

| Capability | MVP permission | Required controls before implementation |
| --- | --- | --- |
| Custom CSS | Approved MVP boundary: forbidden | A later approval must define scoped selector/property allowlists, CSS sanitization, CSP/style-src rules including remote import handling, storage, admin preview isolation, publication review, rollback, public rendering rules, and audit metadata. |
| Custom HTML | Approved MVP boundary: forbidden | A later approval must define allowed tags/attributes, sanitizer behavior, script and event-handler rejection, link/media policy, CSP, storage, admin preview isolation, publication review, rollback, public rendering rules, and audit metadata. |
| Custom JavaScript | Approved MVP boundary: forbidden | A later approval must define execution sandboxing, CSP, network/API permissions, secret access rules, storage, review, admin preview and public runtime isolation, publication, rollback, and audit metadata. |
| External embeds | Approved MVP boundary: forbidden | A later approval must define provider allowlists, iframe sandboxing, CSP frame-src/connect-src rules, privacy and data-sharing disclosure, storage, review, admin preview and public rendering rules, rollback, and audit metadata. |
| Server-side custom code | Approved MVP boundary: forbidden | A later approval must explicitly allow server execution and define isolation, resource limits, filesystem/secret/network restrictions, storage, review, deployment, rollback, monitoring, and audit metadata. |

## Required Future Implementation Tests

Feature plans that implement an approved boundary from this record must add
tests for the relevant rows below. These tests are required before the
implementation may be considered complete; this record itself remains
documentation-only.

| Boundary | Required future tests |
| --- | --- |
| Admin auth and owner trust | Protected routes reject missing/invalid context with `401`; route/body owner, actor, status, and public-id fields cannot override `AdminActorContext`; foreign owned resources return `403`; missing resources return `404`; failed paths do not mutate state or append audit records. |
| In-memory storage | One app/process-scoped state owner is shared across request-scoped adapters; new app/test lifecycle resets state; returned domain objects are isolated copies; concurrent owner/status/public-id/domain/audit mutations are lock-protected and all-or-nothing. |
| Public identifiers | Public ids are opaque, unique in current state, stable across draft/publish status changes, not derived from internal or owner ids, not reused after archive/delete during process lifetime, and collision retry failure leaves no partial resource. |
| Published snapshot fields and future public route | Public serialization includes only approved field groups; draft/private/internal/custom-code fields are rejected or excluded; if a route is later approved, `GET`, `HEAD`, `OPTIONS`, missing, draft, unpublished, archived, cache, and counter behavior match the focused public-route decision. |
| Audit/events | Every approved mutation appends one safe audit record with actor attribution after owner checks; audit append failure prevents the business mutation; failed auth/not-found/permission paths append no audit; per-process order is deterministic under the lock. |
| DNS verification | TXT instructions use `_showcase-constructor.<requested-host>` and `showcase-constructor-verification=<token>`; tokens meet entropy and lifetime rules; owner-triggered recheck honors timeout/retry limits; failed revalidation does not activate routing and marks process-local state according to the approved ownership-loss rule. |
| Custom code deny boundary | Request, storage, admin response, public response, and published snapshot paths reject or exclude custom CSS, HTML, JavaScript, embeds, server-side code, and custom-code metadata; raw code content is never stored, echoed, rendered, executed, published, or audited in MVP. |

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
  verification, public/admin status visibility routes, automatic retry schedules,
  token expiration beyond process lifetime, durable failure-state transition
  policy, and durable domain storage before adding behavior beyond the approved
  DNS TXT ownership proof and owner-triggered process-local recheck state.
- Approved MVP boundary: future test/demo admin mutations, publishing actions,
  domain verification changes, and custom-code changes may use process-local
  in-memory audit records as defined above. Product decision required: choose
  durable database audit records, outbox events, external event streams,
  retention, delivery, and production audit guarantees before claiming durable
  audit/event behavior.
- Approved MVP boundary: user-supplied custom CSS, HTML, JavaScript, external
  embeds, and server-side custom code are forbidden in MVP. Product decision
  required: approve a specific post-MVP category and its controls before
  storing, previewing, rendering, executing, publishing, or publicly exposing any
  user-supplied custom-code content.

## Blocked Feature Plans

- Admin API feature plans beyond the owner-scoped showcase route boundary must
  wait for the final auth provider and any still-unresolved lifecycle behavior,
  durable persistence, and public route method/path decisions; approved test/demo
  mutations must use the process-local in-memory storage and audit boundaries
  above.
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
  must wait for routing, activation, status-visibility, automatic retry,
  expiration beyond process lifetime, durable failure-state policy, and durable
  storage decisions before production custom-domain behavior; approved
  verification changes must use the process-local in-memory audit boundary above
  until durable audit is separately approved.
- Analytics and billing feature plans must wait for explicit MVP scope and data
  exposure decisions.
- Custom code feature plans are blocked for MVP because every user-supplied
  custom-code category is forbidden. A later post-MVP plan must first approve a
  specific category, required controls, and the process-local in-memory audit
  boundary for permission or content changes until durable audit is separately
  approved.
