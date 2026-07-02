# Nuxt Frontend for the FastAPI Course Backend

## Context

The repo currently contains a single service, `backend/` — a FastAPI learning project with:

- **Auth** (`apps/auth`) — email/password registration, JWT access (5 min) + refresh (60 min) token pair, refresh tokens tracked in Redis (single-use, rotated), force-logout-all-devices.
- **Users** (`apps/users`) — `User` model with `is_admin: bool` and `permissions: list[str]` (e.g. `CAN_CREATE_CATEGORY`, `CAN_CREATE_PRODUCT`, `CAN_SEE_USERS`, `CAN_SELF_DELETE`). `GET /users/user-info` currently returns only `id, email, name` (schema `UserCreated`) — **admin/permission flags are not exposed to clients**.
- **Products** (`apps/products`) — `Category` (CRUD) and `Product` (create + get/list only, paginated + searchable via `SearchParamsSchema`), image upload to S3 on product creation.
- **Orders** — one open ("cart") order per user, items adjusted via `POST /orders/change-order-product-quantity` (`product_id`, `quantity`, `mode: increase|decrease|set`). No order history endpoint — only the single currently-open order.
- **Payments** (`apps/payments`) — Stripe Checkout Session creation (`GET /payments/get-payment-url`) and a webhook that closes the order. `success_url`/`cancel_url` are hardcoded to `request.base_url` (the API host itself).

Goal: build a full storefront frontend (browsing, cart, checkout) plus a minimal admin section (category/product creation) using Nuxt, following the user's global rules (`frontend.md`, `folders.md`) with two explicit scope reductions agreed with the user below.

## Decisions Made With The User

- **Scope**: full storefront (catalog, cart, checkout) + admin section for categories/products.
- **i18n**: explicitly **skipped** for this project (overrides the global mandatory-i18n rule, by user's explicit choice).
- **Rendering**: Nuxt SSR/Universal mode.
- **Dev workflow**: frontend runs standalone (`npm run dev`), backend via existing `docker-compose` (`nginx` + `backend1` + `backend2`).
- **UI approach**: Tailwind CSS with a hand-built design system (no Nuxt UI / component-kit dependency).
- **Backend changes**: **none**. The user explicitly declined the two additive backend changes that would have improved UX (see Known Limitations). The frontend must work around them instead of requiring a backend change.
- **API access from dev**: `http://localhost/api` via the existing `nginx` container (load-balances `backend1`/`backend2`), not a direct port.

## Architecture

### BFF pattern via Nitro server routes

The browser never calls FastAPI directly. Every data operation goes through Nuxt's own Nitro server routes (`server/api/*`), which proxy to FastAPI:

```
Browser → Nuxt page (useFetch('/api/...')) → Nitro server route → FastAPI (via nginx) → Postgres/Redis/S3
                                                    ↑
                                    httpOnly cookies (access_token, refresh_token)
```

Rationale:
- **No CORS work needed** — browser only ever talks to Nuxt's own origin; Nuxt-to-FastAPI calls are server-to-server.
- **Tokens stay out of client-side JS** — stored as httpOnly cookies set by the Nitro server (via `h3`'s `setCookie`/`getCookie`), not `localStorage`. Mitigates XSS token theft.
- **Auto-refresh is centralized** — a `server/utils/auth.ts` helper checks access-token expiry before proxying; if expired, it calls `POST /auth/refresh` with the refresh cookie (header `X-Refresh-Token`), stores the new pair, and retries the original call transparently. Pages never handle token refresh themselves.

### State management

- **Pinia** stores: `auth` (current user, derived from a session-check call — see Known Limitations for the admin-flag caveat) and `cart` (current order/cart snapshot + item count badge).
- Data fetching in pages/components uses Nuxt's `useFetch`/`useAsyncData` against the local `/api/*` routes (relative URLs — same-origin, works identically during SSR and client-side navigation).

## Pages & Flows

### Public
| Route | Purpose |
|---|---|
| `/` | Landing: featured categories/products |
| `/products` | Catalog: search (`q`), category filter, sort, pagination |
| `/products/[id]` | Product detail, "Add to cart" |
| `/cart` | Current order: view items, change quantity, remove |
| `/checkout/success`, `/checkout/cancel` | Post-payment landing pages (see limitation below) |
| `/login`, `/register` | Auth forms |
| `/account` | Profile (name/email), "Log out of all devices" (force-logout) |

### Admin
| Route | Purpose |
|---|---|
| `/admin/categories` | List, create, edit, delete (all backend endpoints exist) |
| `/admin/products` | List + create with image upload (multipart). **No edit/delete** — backend has no `PATCH`/`DELETE` for products. |

Admin nav is shown to any logged-in user (see limitation below); actual authorization is enforced server-side by FastAPI's `require_permissions`/`is_admin` checks (403 on denial). This is unchanged, existing backend behavior — the frontend adds no new security boundary and removes none.

### Guest behavior
The cart is tied to an authenticated user (`get_order` depends on `get_current_user`). "Add to cart" for an anonymous visitor redirects to `/login`.

## Known Limitations (accepted, not fixed in this iteration)

These stem from the user's explicit decision not to modify the backend:

1. **No admin/permission flags in `/users/user-info`.** The frontend cannot know in advance whether a logged-in user is an admin or holds specific permissions. Mitigation: show the "Admin" nav entry to all logged-in users; rely entirely on the backend's existing 403 responses, surfaced as a friendly "insufficient permissions" message in the admin UI. This is a UX gap, not a security gap — the backend was already the sole enforcement point.
2. **Stripe `success_url`/`cancel_url` point at the API host, not the frontend.** After paying, the browser lands on the FastAPI host rather than `/checkout/success` on the Nuxt app. Mitigation: the `/cart` page re-checks order status (`GET /orders/` via the proxy) on the browser `visibilitychange` event, so if the user manually navigates back to the store tab, the UI reflects the closed order without depending on the redirect target. This does not fully solve the UX gap — a future backend change (add `FRONTEND_URL` setting, use it in `payments/router.py`) is the real fix, deferred by user request.
3. **No product edit/delete, no order history.** Out of scope because the corresponding backend endpoints don't exist; not being faked client-side.

## Project Structure

```
frontend/
├── app/
│   ├── assets/css/main.css        # Tailwind + design tokens (palette, type scale)
│   ├── components/
│   │   ├── ui/                    # Button, Card, Input, Modal, Badge, Toast, Spinner
│   │   ├── catalog/               # ProductCard, ProductGrid, CategoryFilter, SearchBar
│   │   ├── cart/                  # CartItem, CartSummary
│   │   └── layout/                # Header, Footer, AdminSidebar
│   ├── composables/                # useAuth, useCart, useCatalog, useAdminCatalog
│   ├── layouts/                    # default.vue, admin.vue
│   ├── middleware/                 # auth.ts, admin.ts (client-side UX guard only, not a security boundary)
│   ├── pages/                      # per the tables above
│   ├── stores/                     # auth.ts, cart.ts (Pinia)
│   └── app.vue
├── server/
│   ├── api/
│   │   ├── auth/[...].ts           # login/register/refresh/logout — sets httpOnly cookies
│   │   ├── catalog/...             # products/categories proxy (GET, no token needed)
│   │   ├── cart/...                # order proxy (requires token)
│   │   └── admin/...               # category/product create-update-delete proxy
│   └── utils/
│       ├── backendClient.ts        # $fetch wrapper targeting BACKEND_URL
│       └── auth.ts                 # cookie read/write, auto-refresh-before-proxy logic
├── tests/
│   ├── unit/                       # composables, server/utils (Vitest)
│   └── components/                 # key components (Vitest + @vue/test-utils)
├── nuxt.config.ts
├── package.json
└── .env.example                    # documents BACKEND_URL etc.; actual .env stays at repo root
```

## Environment

Per the global rule against secondary `.env` files, frontend env vars are added to the **existing root** `.env`/`.env.example` (not a new `frontend/.env`):

- `BACKEND_URL=http://localhost/api`

`frontend/package.json`'s dev script points Nuxi at the root file: `nuxi dev --dotenv ../.env`.

## Testing Approach (TDD, per global rule)

- **Vitest** for composables (`useCart`, `useAuth`) and `server/utils` — especially the token-refresh logic in `server/utils/auth.ts`, which is the most fragile piece of the whole system.
- **Component tests** (`@vue/test-utils`) for components with real logic: login/register form validation, cart total calculation.
- Trivial presentational components (`Button`, `Badge`) are not tested — equivalent to "trivial getters/setters" in the global testing rule.
- E2E (Playwright) is out of scope for v1; can be added later as a separate increment.

## Tooling / Modules

- `@pinia/nuxt`, `@vueuse/core`
- `@nuxt/image` (S3-hosted product images)
- Tailwind CSS v4 (no component-kit dependency, per user's UI choice)
- `@nuxt/eslint`
- Icons via `@iconify` / `nuxt-icon`

## Out of Scope for v1

- i18n (explicit user decision, overrides global rule)
- Product edit/delete, order history (no backend support)
- Fixing the Stripe redirect target or exposing admin flags (explicit user decision — backend untouched)
- E2E tests, deployment integration into `docker-compose`/`nginx` (frontend runs standalone for now)
