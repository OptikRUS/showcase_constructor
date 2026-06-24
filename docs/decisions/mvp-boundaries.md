# MVP Boundaries

## Scope

This record is the current decision boundary for the showcase constructor MVP. It
does not implement business code, route registration, runtime configuration,
migrations, or rendering behavior.

### In scope

- The existing `GET /health` endpoint remains the only confirmed public runtime
  surface.
- Decision-first planning for constructor scope, showcase publishing, custom
  domains, analytics, billing, admin API, public storefront behavior, and custom
  code permissions.
- PostgreSQL as the approved durable MVP storage boundary for constructor data,
  drafts, published snapshots, domains, audit trail, and events.
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
| Showcase publishing | Published snapshot response-field boundary and PostgreSQL audit/event boundary approved; publication workflow product decision required | Future public exposure is approved only for the published snapshot field groups listed below. Publication states, publish/unpublish behavior, and rollback remain blocked until focused decisions approve them; future publishing mutations must use the audit/event boundary below. |
| Custom domains | DNS TXT ownership-proof boundary and PostgreSQL domain storage boundary approved; routing and production activation behavior product decision required | Future MVP planning may persist domain records and verification state in PostgreSQL after focused domain behavior decisions approve the route contract. Custom-domain routing, activation after verification, and public status visibility remain blocked until focused decisions approve them; future verification changes must use the audit/event boundary below. |
| Analytics | product decision required | Blocked until event collection, retention, and public/admin visibility are approved. |
| Billing | product decision required | Blocked until paid features, account ownership, and provider integration are approved. |
| Admin API | MVP JWT bearer adapter plus approved protected admin route and PostgreSQL persistence boundaries | Protected owner-scoped admin route classes from `docs/showcase-constructor-tz.md` are approved as non-public MVP route contracts; lifecycle and editing behavior still requires focused decisions, and approved mutations must use the audit/event boundary below. |
| Public storefront | Public published-snapshot reads and non-PII public event ingestion route classes approved | Public `GET /api/v1/public/showcases/resolve`, `GET /api/v1/public/showcases/{public_id}`, and approved event ingestion routes may be registered by future implementation plans; public reads may return only published snapshot data, and event payload schemas remain product decision required. |
| Persistence | Approved MVP boundary: PostgreSQL durable storage | PostgreSQL is the approved durable MVP storage for constructor data, drafts, published snapshots, domains, audit trail, and events. In-memory storage is allowed only in unit tests or test doubles and is not a product persistence layer. |
| Custom code | Approved MVP boundary: partner-controlled frontend `head`/`body` code | Partner custom code for counters, pixels, and external widgets may be stored in drafts and published snapshots as frontend data only. Backend execution, server-side secret/runtime access, server-side custom code, and raw end-user PII handling through custom code are forbidden. |

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
mutations must emit durable PostgreSQL audit records under the audit/event
boundary below.
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
| Admin publish/unpublish actions | `POST /api/v1/showcases/{id}/publish`, `POST /api/v1/showcases/{id}/unpublish` | Not approved | Current admin context required | Approved as protected owner-scoped route classes from `docs/showcase-constructor-tz.md`; publication semantics, snapshot rules, and cache invalidation remain product decision required. |
| Admin clone/archive/restore actions | `POST /api/v1/showcases/{id}/clone`, `POST /api/v1/showcases/{id}/archive`, `POST /api/v1/showcases/{id}/restore` | Not approved | Current admin context required | Approved only for owner-scoped action boundaries in `docs/decisions/admin-api-lifecycle.md`; behavior and the audit/event boundary still apply. |
| Admin preview action | `POST /api/v1/showcases/{id}/preview` | Not approved | Current admin context required | Approved as a protected owner-scoped route class from `docs/showcase-constructor-tz.md`; preview rendering behavior remains product decision required. |
| Admin block management | `GET /api/v1/showcases/{id}/blocks`, `POST /api/v1/showcases/{id}/blocks`, `PATCH /api/v1/showcases/{id}/blocks/{block_id}`, `DELETE /api/v1/showcases/{id}/blocks/{block_id}` | Not approved | Current admin context required | Approved as protected owner-scoped route classes from `docs/showcase-constructor-tz.md`; editable block schema and behavior remain product decision required. |
| Admin offer management | `GET /api/v1/showcases/{id}/offers`, `POST /api/v1/showcases/{id}/offers`, `PATCH /api/v1/showcases/{id}/offers/{offer_id}`, `DELETE /api/v1/showcases/{id}/offers/{offer_id}` | Not approved | Current admin context required | Approved as protected owner-scoped route classes from `docs/showcase-constructor-tz.md`; offer source/import behavior remains product decision required. |
| Admin domain management | `GET /api/v1/showcases/{id}/domains`, `POST /api/v1/showcases/{id}/domains`, `POST /api/v1/showcases/{id}/domains/{domain_id}/verify`, `DELETE /api/v1/showcases/{id}/domains/{domain_id}` | Not approved | Current admin context required | Approved as protected owner-scoped route classes from `docs/showcase-constructor-tz.md`; activation, routing, and status visibility behavior remain product decision required. |
| Admin replacement | `PUT` | Not approved | Current admin context required | Mutation permissions and behavior remain product decision required; any later approval must use the audit/event boundary below. |
| Admin partial updates | `PATCH /api/v1/showcases/{id}` | Not approved | Current admin context required | Approved only for owner-scoped draft patch boundary in `docs/decisions/admin-api-lifecycle.md`; patchable fields beyond the current title update remain product decision required. |
| Admin deletion | `DELETE` | Not approved | Current admin context required | Deletion permissions, recovery needs, and behavior remain product decision required; any later approval must use the audit/event boundary below. |

## Public Data And Identifiers

The public runtime surfaces approved for MVP planning are the existing
`GET /health` response, published-snapshot storefront reads, and approved
non-PII event ingestion routes. This record approves the public identifier
model, response-field boundary, and route classes for future implementation; it
does not register routes or implement endpoints.

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
groups below for the approved public `GET` route classes only.

Public ids are generated by the application from a cryptographically secure
random source using at least 128 bits of entropy, such as `secrets.token_urlsafe`.
Generation must happen inside the storage mutation that creates the public-id
binding, and uniqueness must be checked through the PostgreSQL write boundary,
for example with a transaction plus a unique constraint. A collision retries
generation; repeated collision failure aborts the create/clone operation without
exposing a partial resource.

Public ids are stable for the resource lifetime. Rotation, aliases, redirects,
human-readable slugs, and custom-domain ids are not approved in MVP. A deleted or
archived resource's public id must not be reused by another resource in durable
storage. Draft, unpublished, archived, and missing resources must not resolve
through public storefront reads.

### Public Storefront Route Status

The public storefront `GET` route classes from
`docs/showcase-constructor-tz.md` are approved for future implementation:

- `GET /api/v1/public/showcases/resolve?host=...&path=...`;
- `GET /api/v1/public/showcases/{public_id}`.

Public `GET` returns only an existing published snapshot addressed by an opaque
public id or by an approved host/path resolution. Missing, draft, unpublished,
and archived resources return `404`. Public reads do not expose draft state,
internal database identifiers, owner/admin identifiers, tenant/account
identifiers, private analytics, service credentials, or raw custom-code review
metadata.

Explicit public `HEAD` and app-defined `OPTIONS` behavior remains a guardrail
decision. If `HEAD` is later app-defined, it must mirror the approved `GET`
authorization and existence semantics without a body. If `OPTIONS` is introduced
through middleware, it must not expose private resource existence. Public reads
do not mutate counters, analytics, audit records, or storage state unless a
separate counter/analytics decision approves that mutation path.

### Public Event Route Status

The public event ingestion route classes from `docs/showcase-constructor-tz.md`
are approved only for non-PII event payloads:

- `POST /api/v1/events/showcase-view`;
- `POST /api/v1/events/offer-impression`;
- `POST /api/v1/events/offer-click`;
- `POST /api/v1/events/redirect-click`;
- `POST /api/v1/events/popup`.

Concrete event schemas, retention, aggregation, idempotency, and public/admin
visibility remain `product decision required`. Event ingestion must not accept
loan applications, credit questionnaires, raw end-user PII, service credentials,
or backend-executable custom code.

Approved public fields must be read from the published snapshot shape currently
represented by `src/core/public_config/schemas.py::PublishedPublicConfigSnapshot`
and serialized by `src/api/public_config/schemas.py::PublicConfigResponse`.
Draft data, admin-only data, and storage-private data must not be copied into
that public payload.

| Field class | Public exposure | Rationale |
| --- | --- | --- |
| Public showcase identifier | Approved MVP boundary: opaque public showcase id | Public reads may use `public_id` in `/api/v1/public/showcases/{public_id}` and may expose the same opaque id as published snapshot `id`. |
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
| Published custom `head` code | Approved public data only after publication | Exposes partner-controlled frontend code for counters, pixels, and external widgets as part of the published snapshot. It must not be executed by the backend or receive server-side secrets/runtime access. |
| Published custom `body` code | Approved public data only after publication | Exposes partner-controlled frontend code for counters, pixels, and external widgets as part of the published snapshot. It must not be executed by the backend or receive server-side secrets/runtime access. |
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
| Custom code metadata | Not approved | Public responses may expose only the approved published frontend `head`/`body` code values. Review state, sanitizer state, sandbox settings, private moderation metadata, and backend execution metadata remain blocked. |
| Domain verification status | Not approved for public exposure; protected owner-admin visibility may be approved by a later route plan | DNS TXT verification status may be returned only through future authenticated owner-scoped admin domain management routes after those routes are approved. Public storefront responses must not expose verification status. |

## Persistence

The MVP storage boundary approves PostgreSQL as the durable source of truth for
constructor data, drafts, published snapshots, domains, audit trail, and events.
PostgreSQL-backed implementation may add runtime `DB_*` settings, async
SQLAlchemy/asyncpg infrastructure, Alembic migrations, and concrete
`src/storages` implementations when a focused infrastructure or feature plan
requires them.

The current core storage interface is
`src/core/storages.py::AdminShowcaseStorage`, with `get_by_id()` and
`update_draft()` methods. Future PostgreSQL implementation may add concrete
storage under `src/storages/` and DI provider wiring for that interface when a
use case requires it. Domain verification, audit/event, public snapshot, and
analytics/event storage interfaces should be added only by focused feature plans
that define their business tables and behavior.

In-memory storage is allowed only for unit tests or test doubles. It is not the
product MVP persistence layer, must not be wired as durable runtime storage, and
must not be used to claim publication durability, domain ownership durability,
audit durability, analytics retention, billing records, or multi-process
consistency.

The database transaction boundary is the DI-managed `AsyncSession` Unit of Work.
DI providers own transaction start/end behavior. Storage and use case code must
not call `session.commit()` or `session.begin()`. Storage methods perform
persistence operations, avoid business logic, and return domain schemas rather
than ORM models.

Internal PostgreSQL primary keys are private implementation details. Public
storefront lookup uses opaque public showcase ids or approved host/path
resolution. Authenticated admin ids may be returned only for owned admin
resources under the admin response boundary.

Exact business table design, lifecycle transition behavior, publish/unpublish
semantics, analytics retention, custom-domain activation, final audit/outbox
design, and concrete public event schemas remain `product decision required`.
This record approves the durable backend and storage layer boundary; it does not
create business tables or implement persistence behavior.

| Boundary | MVP decision | Required constraint |
| --- | --- | --- |
| Backend choice | Approved MVP boundary: PostgreSQL durable storage | PostgreSQL is the source of truth for constructor data, drafts, published snapshots, domains, audit trail, and events. |
| Test doubles | Approved only for unit tests and test doubles | In-memory storage may be used in tests, but not as the product runtime persistence layer. |
| Persistence runtime config | Approved for PostgreSQL infrastructure | Runtime database settings use project config rules and `DB_*` environment variables; secrets remain secret settings. |
| Storage layer | Approved for concrete PostgreSQL storage under `src/storages/` | Implementations must use the `storages` layer name; do not introduce `repositories` or `repos`. |
| Core storage interfaces | Existing interface acknowledged | `src/core/storages.py::AdminShowcaseStorage` already defines the admin showcase storage interface. Add or change core interfaces only when a use case requires them. |
| Ownership model | Core/use-case owned | Storage preserves owner/partner fields, but access decisions remain in core use cases using the current admin context; storage must not become the permission layer. |
| Migrations | Approved for PostgreSQL infrastructure | Alembic migrations may be added by focused infrastructure or schema plans. Business migrations require approved table/schema decisions. |
| Transaction boundary | Project constraint approved | DI providers own the `AsyncSession` Unit of Work; storage and use case code must not call `session.commit()` or `session.begin()`. |
| Storage behavior | Project constraint approved | Storage methods perform persistence operations, avoid business logic, and return domain schemas rather than ORM models. |

## Domain Verification

The MVP domain verification method is DNS TXT ownership proof. A future
custom-domain implementation may generate an opaque verification token, show the
owner DNS instructions for a TXT record, check that TXT record for the requested
host, and update PostgreSQL-backed verification state after the focused route
behavior is approved. This boundary does not approve CNAME validation, HTTP file
validation, email verification, provider API checks, manual review,
custom-domain routing, or production publication on a custom domain.

The verification token must be generated by the application as an opaque,
unguessable value. It must not contain or derive from internal storage ids,
owner/admin identifiers, partner ids, tenant/account ids, emails, usernames,
profile identifiers, custom-code metadata, or public slugs. Token and status
storage may use the approved PostgreSQL durable storage boundary. File storage,
external-provider state, and runtime DNS provider settings remain blocked unless
a focused feature decision approves them.

The approved TXT record name is `_showcase-constructor.<requested-host>`, where
`<requested-host>` is the exact normalized host being verified. The approved TXT
value format is `showcase-constructor-verification=<token>`. The token is
generated with a cryptographically secure random source using at least 192 bits
of entropy, such as `secrets.token_urlsafe(32)`.

Token lifetime is durable until the owner explicitly regenerates the token or a
later expiration policy is approved. There is no automatic expiration,
background refresh, or scheduled retry in MVP. Regeneration invalidates the
previous token for that domain state.

Verification checks are owner-triggered revalidation attempts against the current
TXT record. A single recheck may perform at most two resolver attempts with a
per-attempt timeout of two seconds. Timeout, NXDOMAIN, resolver error, or missing
matching token leaves the domain unverified or moves an already verified
durable state to ownership-lost/pending recheck; it must not activate or route
traffic. DNS resolver library/package selection remains an implementation plan
concern and must follow dependency rules if a new dependency is required.

DNS verification proves only control of the requested host at the time of the
latest successful recheck. It does not approve custom-domain route activation,
public storefront host routing, domain detachment behavior, production
publication, public status exposure, or final activation semantics.

| Verification question | MVP decision | Feature plan boundary |
| --- | --- | --- |
| Ownership proof method | Approved MVP boundary: DNS TXT record at `_showcase-constructor.<requested-host>` containing `showcase-constructor-verification=<token>` | Future custom-domain verification planning may implement TXT lookup/check behavior only; CNAME, HTTP file, email, provider API, and manual verification remain blocked. |
| Verification token format and storage | Approved MVP boundary: opaque token with at least 192 bits of randomness stored in PostgreSQL domain verification state | File storage, external-provider state, and token values derived from private identifiers are not approved. |
| Retry, expiration, and failure handling | Approved MVP boundary for owner-triggered recheck only | Each recheck may use at most two resolver attempts with two-second per-attempt timeout. No automatic retry schedule, durable lockout, background job, or automatic expiration is approved. |
| Ownership loss and revalidation | Approved MVP boundary: latest recheck controls durable verification state | Failed recheck or missing token must not activate routing and may mark verification as pending/lost. Final activation and detachment semantics remain product decision required. |
| Activation after successful verification | product decision required | Verification may establish ownership state only. Custom-domain routing, production activation, Host-based public rendering, domain detachment, and publication behavior remain blocked for public storefront and custom-domain feature plans. |
| Public/admin visibility of verification status | Public visibility not approved; authenticated owner-admin visibility product decision required by route | Verification status must not appear in public storefront responses. A future protected owner-scoped admin domain route may request approval to return status values such as pending, verified, failed, active, or disabled. |

## Audit And Events

The MVP audit/event boundary approves PostgreSQL durable storage for audit
records and approved public event ingestion. Exact table shape, retention,
outbox/event-stream integration, aggregation, and admin analytics visibility
remain `product decision required`.

Every approved audited mutation must write an audit record in the same
request/use-case flow after the owner and permission checks succeed. Records may
be exposed only to authenticated admin tooling approved by a later feature plan;
this decision does not approve public audit data, public verification status, or
private actor identifiers in storefront responses.

Audit append is mandatory for every approved audited mutation, not best-effort.
For PostgreSQL MVP behavior, mutation and audit append must share the same
database Unit of Work when they are part of one business command. If the audit
record cannot be appended, the business mutation must not become visible and the
request must fail without a partial state change.

Audit actor attribution records the authenticated `user_id` and `partner_id`
from `AdminActorContext` for admin-triggered mutations. Domain verification
actions triggered by an owner-admin use the same actor context; system or
background actors are not approved in MVP. Audit metadata must not include
secrets, custom-code contents, private service settings, or full draft/published
snapshot payloads.

Audit ordering is database write order for the relevant storage model. Global
cross-system ordering, exactly-once delivery, idempotency keys, duplicate
suppression, transactional outbox delivery, external event streams, and retention
periods remain `product decision required`. If a client retries a completed
mutation, a later implementation must either append a second audit record or
first add an idempotency decision.

| Audited action class | Durability decision | Feature plan boundary |
| --- | --- | --- |
| Admin create showcase | Approved MVP boundary: PostgreSQL audit record | Future owner-scoped `POST /api/v1/showcases` implementation must record actor context, owned showcase id, action type, timestamp, and allowed response metadata. Exact table fields remain product decision required. |
| Admin patch draft showcase | Approved MVP boundary: PostgreSQL audit record | Future owner-scoped `PATCH /api/v1/showcases/{id}` implementation must record actor context, owned showcase id, action type, timestamp, and changed field names or safe metadata. Draft content diffs and private settings remain blocked. |
| Admin clone showcase | Approved MVP boundary: PostgreSQL audit record | Future owner-scoped clone implementation must record actor context, source showcase id, cloned showcase id, action type, timestamp, and safe metadata. Copy semantics remain product decision required. |
| Admin archive showcase | Approved MVP boundary: PostgreSQL audit record | Future owner-scoped archive implementation must record actor context, owned showcase id, action type, timestamp, and safe archive metadata. Archive behavior remains product decision required. |
| Admin restore showcase | Approved MVP boundary: PostgreSQL audit record | Future owner-scoped restore implementation must record actor context, owned showcase id, action type, timestamp, and safe restore metadata. Restore behavior remains product decision required. |
| Admin unarchive alias | Blocked | The admin lifecycle boundary selects `POST /api/v1/showcases/{id}/restore`; no separate unarchive audit event is approved unless the alias is later approved. |
| Showcase publishing changes | Approved MVP boundary: PostgreSQL audit record | If a later publishing decision approves publish, unpublish, rollback, or republish behavior, each mutation must record actor context, showcase id, action type, timestamp, and safe snapshot metadata. Publishing behavior remains product decision required. |
| Domain verification changes | Approved MVP boundary: PostgreSQL audit record | Future DNS TXT verification requests, owner-triggered rechecks, and safe status updates must record actor context when present, domain identifier, action type, timestamp, and safe verification metadata. Activation, expiration, automatic retry policy, and public/admin status visibility remain product decision required. |
| Custom `head`/`body` code changes | Approved MVP boundary: PostgreSQL audit record | Future custom-code changes must record actor context, showcase id, target location, action type, timestamp, and safe metadata. Raw code content, secrets, raw end-user PII, and backend execution metadata must not be stored in audit records. |
| Server-side custom code changes | Blocked | Server-side custom code remains forbidden. No backend execution, server-side secret/runtime access, or server-executed custom-code audit event is approved. |
| Public event ingestion | Approved only for non-PII MVP event payloads | Event records may support showcase views, offer impressions, offer clicks, redirect clicks, and popup events. Concrete schemas, retention, aggregation, idempotency, and visibility remain product decision required. |
| Billing-relevant events | product decision required | Billing event collection, retention, and public/admin visibility remain blocked until a billing decision approves them. |

## Custom Code Permissions

The MVP custom-code permission boundary allows partner-controlled custom code
only in the `head` and `body` frontend publication locations for counters,
pixels, and external widgets. The code may be stored in drafts, previewed for an
authorized owner, and copied into the public snapshot only after publication.
The backend stores and publishes it as data; it must never execute the code.

Custom code must not receive server-side secrets, filesystem access,
server-side runtime access, or backend network/API capabilities. The backend
must not accept or process raw end-user PII through custom code, and public
event ingestion must not become a hidden PII collection path for custom scripts.
Server-side custom code remains forbidden in MVP.

Future plans that implement custom-code fields must define owner-only edit
authorization, preview behavior, publication behavior, warnings, audit metadata,
and public serialization. Review state, sanitizer state, sandbox settings, and
moderation metadata are not public response fields unless a later decision
explicitly approves them.

| Capability | MVP permission | Required controls before implementation |
| --- | --- | --- |
| Custom `head` frontend code | Approved MVP boundary | May be stored and published for counters, pixels, and external widgets. Must be owner-editable only, audited, previewable, and published only as frontend data. No backend execution, server-side secrets, or raw end-user PII handling. |
| Custom `body` frontend code | Approved MVP boundary | May be stored and published for counters, pixels, and external widgets. Must be owner-editable only, audited, previewable, and published only as frontend data. No backend execution, server-side secrets, or raw end-user PII handling. |
| Custom CSS/HTML/JavaScript outside approved `head`/`body` fields | product decision required | Any additional field, block type, sanitizer policy, sandbox setting, or publication path requires a focused decision and controls before implementation. |
| External embeds through approved `head`/`body` code | Approved only as frontend partner code | Provider allowlists, iframe sandboxing, CSP frame/connect policies, and privacy disclosures remain implementation controls for a focused custom-code feature plan. |
| Server-side custom code | Blocked | Server execution, filesystem access, secret access, backend runtime access, deployment hooks, and backend network/API capabilities are forbidden in MVP. |

## Required Future Implementation Tests

Feature plans that implement an approved boundary from this record must add
tests for the relevant rows below. These tests are required before the
implementation may be considered complete; this record itself remains
documentation-only.

| Boundary | Required future tests |
| --- | --- |
| Admin auth and owner trust | Protected routes reject missing/invalid context with `401`; route/body owner, actor, status, and public-id fields cannot override `AdminActorContext`; foreign owned resources return `403`; missing resources return `404`; failed paths do not mutate state or append audit records. |
| PostgreSQL storage | Database-backed storage uses the DI `AsyncSession` Unit of Work, returns domain schemas rather than ORM models, keeps internal primary keys private, and leaves state unchanged on failed business commands. |
| Public identifiers | Public ids are opaque, unique in durable storage, stable across draft/publish status changes, not derived from internal or owner ids, not reused after archive/delete, and collision retry failure leaves no partial resource. |
| Published snapshot fields and public route | Public serialization includes only approved field groups and published custom `head`/`body` frontend code; draft/private/internal fields, custom-code metadata, and server-side execution metadata are rejected or excluded; `GET`, missing, draft, unpublished, archived, cache, and counter behavior match the focused implementation decision. |
| Public event ingestion | Event routes reject raw end-user PII, service credentials, backend-executable custom code, and unapproved event shapes; failed event writes do not block user redirects where redirect behavior applies. |
| Audit/events | Every approved mutation appends one safe PostgreSQL audit record with actor attribution after owner checks; audit append failure prevents the business mutation; failed auth/not-found/permission paths append no audit. |
| DNS verification | TXT instructions use `_showcase-constructor.<requested-host>` and `showcase-constructor-verification=<token>`; tokens meet entropy and lifetime rules; owner-triggered recheck honors timeout/retry limits; failed revalidation does not activate routing and marks durable verification state according to the approved ownership-loss rule. |
| Custom code frontend boundary | Request, storage, admin response, public response, and published snapshot paths allow only owner-controlled frontend `head`/`body` code; backend execution, server-side secret/runtime access, raw end-user PII handling through custom code, and server-side custom code are rejected. |

## Blocking Decisions

- Product decision required: choose the external admin API auth-provider
  integration, refresh/session activation model, internal-admin override,
  production replacement criteria, and still-unresolved lifecycle behavior
  details before adding management behavior beyond the owner-scoped route
  boundary approved in `docs/decisions/admin-api-lifecycle.md`.
- Product decision required: define exact public storefront error/cache behavior,
  counter mutation behavior, and concrete public event schemas before adding
  those behaviors. The public `GET` and non-PII event route classes are approved,
  but implementation still must satisfy the published-snapshot and PII
  boundaries above.
- Product decision required: choose exact business table design, lifecycle
  transition behavior, publish/unpublish semantics, analytics retention,
  custom-domain activation, final audit/outbox design, and concrete public event
  schemas before adding those business behaviors. PostgreSQL is already the
  approved durable backend.
- Product decision required: choose custom-domain routing, activation after
  verification, public/admin status visibility routes, automatic retry schedules,
  token expiration policy, and durable failure-state transitions before adding
  behavior beyond the approved DNS TXT ownership proof and owner-triggered
  recheck state.
- Approved MVP boundary: future admin mutations, publishing actions, domain
  verification changes, and custom-code changes must use PostgreSQL audit
  records as defined above. Product decision required: choose transactional
  outbox behavior, external event streams, retention, delivery, and analytics or
  billing visibility before implementing those surfaces.
- Approved MVP boundary: partner custom `head` and `body` frontend code is
  allowed for counters, pixels, and external widgets. Product decision required:
  approve any additional custom-code category or control surface before storing,
  previewing, rendering, executing, publishing, or publicly exposing it.

## Blocked Feature Plans

- Admin API feature plans beyond the owner-scoped route boundary must wait for
  the final auth provider and any still-unresolved lifecycle behavior. Approved
  mutations must use the PostgreSQL storage and audit boundaries above.
- Public storefront feature plans may register the approved public `GET` route
  classes and must return only approved published snapshot data. Counter
  mutation, exact cache behavior, and event schemas still require focused
  decisions before implementation.
- Durable persistence infrastructure plans may add PostgreSQL settings,
  dependencies, Alembic layout, and DI Unit of Work wiring without business
  tables. Business schema plans must wait for table, ownership, and behavior
  decisions.
- Custom domain feature plans may use the approved DNS TXT ownership-proof
  method and PostgreSQL verification state, but must wait for routing,
  activation, status-visibility, automatic retry, expiration policy, and
  failure-state transition decisions before production custom-domain behavior.
- Analytics and billing feature plans must wait for explicit MVP scope and data
  exposure decisions.
- Custom code feature plans may implement only partner-controlled frontend
  `head` and `body` code for counters, pixels, and external widgets. Any
  server-side custom code, backend execution, secret/runtime access, raw
  end-user PII handling, or additional custom-code category remains blocked
  until a focused decision approves it.
