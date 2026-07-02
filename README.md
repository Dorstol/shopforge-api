# ShopForge API

A FastAPI backend for an online store — authentication, product catalog, cart/orders and Stripe payments, built with an async SQLAlchemy + Redis + S3 stack and deployed behind nginx with load-balanced backend instances.

## Features

- **Auth** — email/password registration, JWT access + refresh token pairs (refresh tokens tracked in Redis, single-use and rotated), force-logout of all devices.
- **Users** — accounts with `is_admin` flag and fine-grained permissions (e.g. `CAN_CREATE_CATEGORY`, `CAN_CREATE_PRODUCT`, `CAN_SEE_USERS`, `CAN_SELF_DELETE`).
- **Catalog** — categories and products (CRUD for categories, paginated + searchable product listing), product images uploaded to S3.
- **Cart & Orders** — one open ("cart") order per user, quantities adjusted via increase/decrease/set operations.
- **Payments** — Stripe Checkout session creation and webhook handling to close paid orders.
- **Caching** — Redis-backed response caching via `fastapi-cache2`.
- **Observability** — Sentry error tracking and BetterStack log shipping.
- **API docs** — interactive Scalar UI, generated from the OpenAPI schema.
- **Deployment** — Dockerized, two backend instances load-balanced by nginx; migrations run automatically on startup via Alembic.

## Tech Stack

FastAPI · SQLAlchemy 2.0 (async) · PostgreSQL · Alembic · Redis · S3 · Stripe · JWT (PyJWT) · Sentry · BetterStack · nginx · Docker Compose

## Project Structure

```
backend/
  app/
    apps/
      auth/         # registration, login, JWT/refresh tokens
      users/         # user accounts & permissions
      products/      # categories, products, orders
      payments/       # Stripe checkout & webhooks
      services/      # Redis, S3, Sentry, BetterStack integrations
      core/          # shared base models, CRUD helpers, dependencies
    migrations/       # Alembic migrations
    settings.py
    app_factory.py
    main.py
  Dockerfile
nginx/                # reverse proxy / load balancer config
documentation/         # MkDocs project docs
docs/                  # design specs
docker-compose.yaml
```

## API Overview

| Prefix | Purpose |
|---|---|
| `/auth` | register, login, refresh, force-logout |
| `/users` | current user info, user listing |
| `/categories` | category CRUD |
| `/products` | product creation & listing |
| `/orders` | view cart, change item quantity |
| `/payments` | Stripe checkout URL, payment webhook |

Full interactive documentation is available at `/api/scalar` when `DEBUG=true`.

## Getting Started

1. Copy `.env.example` to `.env` and fill in the values (PostgreSQL, Redis, S3, Stripe, Sentry, BetterStack, JWT secret).
2. Start the stack:

   ```bash
   make up
   ```

   This builds and runs two backend instances (`backend1`, `backend2`) behind nginx, running Alembic migrations on boot.

3. Useful commands:

   ```bash
   make down     # stop the stack
   make build    # rebuild images
   make bash     # shell into backend1
   make logs     # tail backend1 logs
   make docs     # serve MkDocs documentation at :8010
   ```

4. Database migrations (run inside the backend container, see `backend/app/Makefile`):

   ```bash
   make mm msg="add products table"   # autogenerate a migration
   make m                              # apply migrations
   ```

## Development

- Linting/formatting via `ruff` and `isort`, enforced through `pre-commit` (`.pre-commit-config.yaml`).
- API schema and Scalar docs are served automatically by FastAPI; MkDocs-based project documentation lives under `documentation/`.
