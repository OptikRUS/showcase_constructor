# Draft Constructor Editing Boundary

## Status

Decision-first guardrail. This record approves the minimal authenticated
owner-admin draft editing boundary for showcase settings, blocks, and offers. It
does not implement application code, route registration, migrations, storage,
runtime configuration, dependencies, or public storefront behavior.

This record narrows the constructor-editing items left as
`product decision required` in `docs/decisions/mvp-boundaries.md` and
`docs/decisions/admin-api-lifecycle.md`. Unresolved publishing, audit/outbox,
and external offer-source details remain blocked until later focused decisions.

## Approved Draft Editing Surface

Draft editing is approved only for authenticated owner-admin routes. No route in
this boundary is public, and no app-defined admin `HEAD` or `OPTIONS` route is
approved here.

Every approved endpoint must resolve the current owner through the existing admin
JWT context, pass the already-validated `AdminActorContext` to exactly one use
case, and enforce `context.partner_id` ownership before returning or mutating
draft data. Failed `401`, `403`, and `404` paths must not mutate draft data,
published snapshots, or audit state.

| Operation | Candidate method and path | Public access | Status |
| --- | --- | --- | --- |
| Patch draft showcase settings | `PATCH /api/v1/showcases/{id}` | Not approved | Approved for authenticated owner-admin draft settings, text, and banner edits only. |
| List draft blocks | `GET /api/v1/showcases/{id}/blocks` | Not approved | Approved for authenticated owner-admin block inspection only. |
| Create draft block | `POST /api/v1/showcases/{id}/blocks` | Not approved | Approved for authenticated owner-admin draft block creation only. |
| Patch draft block | `PATCH /api/v1/showcases/{id}/blocks/{block_id}` | Not approved | Approved for authenticated owner-admin draft block edits only. |
| Delete draft block | `DELETE /api/v1/showcases/{id}/blocks/{block_id}` | Not approved | Approved for authenticated owner-admin draft block removal only. |
| List draft offers | `GET /api/v1/showcases/{id}/offers` | Not approved | Approved for authenticated owner-admin offer inspection only. |
| Create draft offer | `POST /api/v1/showcases/{id}/offers` | Not approved | Approved for authenticated owner-admin manual/admin draft offer creation only. |
| Patch draft offer | `PATCH /api/v1/showcases/{id}/offers/{offer_id}` | Not approved | Approved for authenticated owner-admin draft offer edits only. |
| Delete draft offer | `DELETE /api/v1/showcases/{id}/offers/{offer_id}` | Not approved | Approved for authenticated owner-admin draft offer removal only. |

## Minimal Draft Schema Boundary

The durable schema may use explicit owner-scoped showcase records plus separate
draft block and draft offer rows, or an equivalent PostgreSQL shape that
preserves the same ownership and draft/published separation constraints. Route
and response identifiers are string application ids. Internal PostgreSQL primary
keys remain private implementation details.

| Draft area | Approved editable data | Required constraints |
| --- | --- | --- |
| Showcase settings | `designId`, `colorScheme`, background/card/widget/offers/text/USP/CTA colors, CTA hover/click state colors, `fontFamily`, `offersPlacement`, `offersMobilePlacement`, `uspPlacement`, alignment, popup/widget offsets, `trackingDomain`, logo, favicon, desktop banner, mobile banner, mini banner, title, subtitle, CTA text, meta title, meta description, and fallback text. | Mutations update draft data only. Missing fields mean no change; explicit nullable clearing is allowed only where the implementation schema permits it. |
| Draft blocks | String `block_id`, type, order, visibility, title, subtitle, desktop settings, mobile settings, and type-specific display data. | Supported block types are `hero`, `offers`, `banner`, `banner_card`, `advantages`, `legal_footer`, `popup_offers`, `custom_html`, and `calculator`. |
| Draft offers | String `offer_id`, enablement, manual order, block assignment, CTA override, USP override, fields as `{key, value, visible}`, categories, logo URLs, display names, site name, CPA URL, legal entity, INN, and optional `erid`. | Disabled offers and hidden fields remain visible to the owner-admin draft API but are not approved for public snapshot exposure. |
| Published snapshots | None. | Draft editing must not mutate `PublishedPublicConfigSnapshot`, public config schemas, public config routes, or any published snapshot table/column. |

## Owner-Admin Response Boundary

This response boundary applies only after the authenticated owner check
succeeds. It does not approve public storefront exposure.

| Field group | Owner-admin response boundary |
| --- | --- |
| Showcase id | Approved as the admin route/resource id for owned resources only. |
| Draft settings fields | Approved for owner-admin draft responses using boundary-schema aliases such as `designId`, `colorScheme`, `fontFamily`, `textTitle`, `textSubtitle`, `textButton`, `metaTitle`, `metaDescription`, `imageBannerDesktop`, `imageBannerMobile`, `imageBannerMini`, and `fallbackText`. |
| `block_id` | Approved only as an owner-admin draft block identifier after the showcase owner check succeeds. Public storefront responses must not expose internal draft block ids. |
| Block draft fields | Approved for owner-admin draft responses: type, order, visibility, title, subtitle, desktop settings, mobile settings, and type-specific data. |
| `offer_id` | Approved only as an owner-admin draft offer identifier after the showcase owner check succeeds. Public storefront responses must not expose internal draft offer ids. |
| Offer draft fields | Approved for owner-admin draft responses: enablement, manual order, block assignment, CTA and USP overrides, visible and hidden fields, categories, logo URLs, display names, site name, CPA URL, legal entity, INN, and `erid`. |
| Owner/admin identifiers | Owner/admin emails, usernames, profile ids, tenant/account ids unrelated to the current owner boundary, and foreign-owner data are blocked. |
| Internal storage fields | Internal PostgreSQL primary keys, audit internals, storage metadata, service credentials, and source-system reconciliation data are blocked. |

## Draft And Public Separation

Draft settings, draft blocks, draft offers, disabled offers, hidden offer fields,
custom HTML, calculator configuration, fallback text, and draft custom code are
owner-admin data until a later publish flow copies approved public fields into a
published snapshot.

Public reads may continue to return only the published snapshot fields approved
in `docs/decisions/mvp-boundaries.md`. A draft update must not change public
config responses, cache state, publication status, or public event behavior.

Disabled offers must be persisted in draft with `enabled: false` so an owner can
continue editing them. Excluding disabled offers, hidden fields, and draft-only
block metadata from public snapshots belongs to the later approved publish
projection behavior.

## Custom HTML And Calculator Boundary

`custom_html` and `calculator` draft block data may be stored as frontend data
only. The backend must never execute custom HTML, JavaScript, calculator logic,
partner scripts, or widget code from these draft blocks.

This record does not approve server-side custom code, server-side secrets,
filesystem access, backend runtime access, backend network/API access, raw
end-user PII handling, sanitizer policy, sandbox policy, CSP policy, or public
exposure for these blocks. Those controls remain `product decision required`
before production public rendering can rely on them.

## Required Product And Security Decisions

| Decision area | Current boundary |
| --- | --- |
| Auth and ownership | Approved: all draft editing routes are protected owner-admin routes using the current admin JWT context and core owner checks. |
| Minimal draft schema | Approved: settings, blocks, and offers may be stored in PostgreSQL using the field groups above while preserving private internal primary keys. |
| Owner-admin identifiers | Approved: `showcase_id`, `block_id`, and `offer_id` may be returned only to the authenticated owner after the owner check succeeds. |
| Draft-only mutation | Approved: settings, block, and offer mutations update draft state only and must not mutate published snapshots or public config responses. |
| Custom HTML and calculator data | Approved only as stored frontend draft data. Backend execution and server-side runtime access are blocked. |
| Audit/outbox shape | product decision required: final audit table fields, safe changed-field metadata, retention, idempotency, transactional outbox behavior, delivery, and external event streams. |
| External offer source/import/sync | product decision required: source-system ids, import flows, reconciliation, CPA-network sync, automatic offer refresh, and source-of-truth conflict handling. |
| Publish/unpublish activation | product decision required: publish, unpublish, rollback, cache invalidation, snapshot activation, public projection, and public event consequences. |
| Public projection details | product decision required: final rules for copying enabled offers, visible fields, public block data, custom HTML/calculator data, and custom code into a published snapshot. |
| Analytics and billing visibility | product decision required: event schemas, aggregation, retention, billing relevance, and admin/public visibility. |

## Implementation Boundary

Future implementation tasks may add focused migrations, storage methods, use
cases, boundary schemas, endpoints, DI wiring, and tests for the approved draft
editing surface above. They must keep endpoints thin, delegate each endpoint to
one use case, keep authorization in core use cases, use concrete PostgreSQL
storage under `src/storages`, and rely on the DI-managed database Unit of Work.

This record does not allow:

- exposing draft data through public config APIs;
- adding publish, unpublish, preview, analytics, billing, custom-domain, or
  external offer-sync behavior;
- executing `custom_html`, `calculator`, custom JavaScript, or partner code on
  the backend;
- exposing internal database ids, owner/admin profile data, tenant/account ids,
  foreign-owner data, audit internals, service credentials, or source-system
  reconciliation data.
