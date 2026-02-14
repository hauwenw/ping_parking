# Tech Stack Plan — Ping Parking Management System

**Date**: 2026-02-14
**Decision**: Plan B — Python/FastAPI Backend + Next.js Frontend
**Status**: Approved

## Architecture Overview

```
┌─────────────────┐      HTTPS       ┌─────────────────────┐      PostgreSQL    ┌──────────────────┐
│   Next.js 14    │◄────────────────►│   FastAPI (Docker)   │◄──────────────────►│  Supabase Free   │
│  + shadcn/ui    │                  │   Python 3.11        │                    │  (DB-only)       │
│  + Tailwind CSS │                  │   SQLAlchemy + GORM  │                    │  PostgreSQL 15   │
└─────────────────┘                  └─────────────────────┘                    └──────────────────┘
     Vercel Free                        Fly.io ($3-5/mo)                         $0/mo (free tier)
                                        Hong Kong region
```

## Stack Components

### Backend: Python/FastAPI

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | FastAPI | 0.110+ | Async REST API |
| **ORM** | SQLAlchemy | 2.0+ | Database operations |
| **Migrations** | Alembic | latest | Auto-generated schema migrations |
| **Validation** | Pydantic | 2.0+ | Request/response validation |
| **Auth** | python-jose | latest | Self-managed JWT (1-3 admin users) |
| **Database Driver** | asyncpg | latest | Async PostgreSQL driver |
| **Testing** | pytest + testcontainers | latest | Integration tests with real Postgres |
| **ASGI Server** | uvicorn | latest | Production server |

### Frontend: Next.js

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | Next.js | 14 | React SSR/SSG |
| **Language** | TypeScript | 5.x | Type safety |
| **UI Components** | shadcn/ui | latest | Production-ready components |
| **Styling** | Tailwind CSS | 3.x | Utility-first CSS |

### Database: Supabase PostgreSQL (Free Tier)

| Feature | Detail |
|---------|--------|
| **Usage** | Database-only (no PostgREST, no Supabase Auth, no RLS) |
| **Connection** | Session mode via Supavisor (port 5432) for prepared statement support |
| **Connection String** | `postgresql://postgres.[ref]:[pass]@aws-0-[region].pooler.supabase.com:5432/postgres` |
| **Storage limit** | 500 MB (estimated usage: ~25 MB Year 1, ~75 MB Year 3) |
| **Bandwidth limit** | 2 GB/mo (estimated usage: ~75 MB/mo) |
| **MAU limit** | 50,000 (actual: 1-3 admin users) |

### Hosting & Infrastructure

| Component | Platform | Tier | Monthly Cost |
|-----------|----------|------|-------------|
| **Backend API** | Fly.io (Hong Kong region) | Shared CPU, 256MB | $3-5 |
| **Frontend** | Vercel | Free (Hobby) | $0 |
| **Database** | Supabase | Free | $0 |
| **Domain** | TBD | — | ~$1.25 |
| **Total** | | | **$4-6/mo** |

### Why Fly.io Over Railway

| Factor | Fly.io (chosen) | Railway (backup) |
|--------|-----------------|------------------|
| **APAC region** | Hong Kong (<10ms to Taiwan) | US-only (150-200ms) |
| **Always-on** | Config: `min_machines_running=1` | Default on Hobby |
| **Cost** | $3-5/mo | $5/mo |
| **Portability** | Docker = trivial to switch | Docker = trivial to switch |

Railway remains a viable backup. Both connect to external Supabase with no restrictions. Switching is ~15 minutes (same Dockerfile, new platform).

## Key Design Decisions

### 1. Supabase as DB-Only (No Lock-in)

We use Supabase **only** for free managed PostgreSQL. No PostgREST API, no Supabase Auth, no RLS policies. Benefits:
- Zero vendor lock-in — swap to any PostgreSQL provider by changing `DATABASE_URL`
- All business logic in FastAPI (testable, debuggable Python code)
- Auth handled by self-managed JWT in FastAPI middleware
- Audit logging in application layer, not database triggers

### 2. Self-Managed JWT Auth

For 1-3 admin users, self-managed JWT is simpler than any auth service:
- ~50 lines of middleware code
- Admin accounts stored in `admin_users` table (or use Supabase Auth just for user management)
- Token issued on login, validated on every request
- No external auth dependency

### 3. Alembic Auto-Migrations

SQLAlchemy models are the source of truth. Alembic auto-generates migration files:
```bash
alembic revision --autogenerate -m "add customers table"
alembic upgrade head
```
This saves ~8 hours over writing 70+ SQL migration files manually.

### 4. Dockerized Backend

Backend ships as a Docker container:
- Consistent across dev/staging/prod
- Interchangeable hosting (Fly.io ↔ Railway ↔ any Docker host)
- Image size: ~180-250 MB (acceptable for this use case)
- Startup time: 1-2 seconds

## Project Structure

### Backend (FastAPI)

```
ping-parking-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   ├── config.py               # Settings (pydantic-settings)
│   ├── database.py             # SQLAlchemy engine/session
│   ├── dependencies.py         # Dependency injection (auth, db)
│   ├── models/                 # SQLAlchemy models (12 tables)
│   │   ├── __init__.py
│   │   ├── customer.py
│   │   ├── space.py
│   │   ├── agreement.py
│   │   ├── payment.py
│   │   ├── tag.py
│   │   ├── site.py
│   │   └── system_log.py
│   ├── schemas/                # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── customer.py
│   │   └── ...
│   ├── api/                    # Route handlers
│   │   ├── __init__.py
│   │   ├── customers.py
│   │   ├── spaces.py
│   │   ├── agreements.py
│   │   └── ...
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── customer_service.py
│   │   ├── agreement_service.py
│   │   └── audit_logger.py
│   └── utils/
│       ├── auth.py             # JWT middleware
│       ├── validators.py       # Taiwan phone, TWD format
│       └── errors.py           # Business error classes (Chinese)
├── alembic/                    # Database migrations
│   ├── versions/
│   └── env.py
├── tests/
│   ├── conftest.py             # Fixtures, testcontainers setup
│   ├── test_customers.py
│   └── ...
├── Dockerfile
├── requirements.txt
├── pyproject.toml
└── alembic.ini
```

### Frontend (Next.js) — Separate Repo or Monorepo

```
ping-parking-web/
├── app/
│   ├── login/page.tsx
│   ├── admin/
│   │   ├── agreements/page.tsx   # Default landing page
│   │   ├── customers/page.tsx
│   │   ├── spaces/page.tsx
│   │   └── settings/page.tsx
│   └── layout.tsx
├── components/                   # shadcn/ui + custom
├── lib/
│   ├── api-client.ts             # Typed HTTP client for FastAPI
│   ├── auth.ts                   # JWT token management
│   └── utils/                    # Formatters (TWD, dates, phones)
├── public/
└── ...
```

## Cost Comparison (Why This Plan Won)

| Plan | Monthly Cost | Time to MVP | Vendor Lock-in |
|------|-------------|-------------|----------------|
| ~~Plan A: Next.js + Supabase~~ | $0-20 | ~6 weeks | High |
| **Plan B: FastAPI + Supabase DB** | **$4-6** | **~8 weeks** | **None** |
| ~~Plan C: Go/Gin + Supabase DB~~ | $4-6 | ~9 weeks | None |

## Estimated MVP Timeline

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Setup + Docker + CI | Project structure, Dockerfile, Fly.io deploy | 4 hrs |
| DB models + migrations | 12 SQLAlchemy models + Alembic | 8 hrs |
| Auth middleware | JWT login/validate + admin users | 4 hrs |
| Audit logging | System log service + integration | 6 hrs |
| CRUD endpoints | 12 entities × 4 endpoints | 24 hrs |
| Business logic | Agreement lifecycle, pricing, double-booking | 12 hrs |
| Error handling + i18n | Traditional Chinese messages, validation | 4 hrs |
| Testing | Integration tests for critical paths | 12 hrs |
| Frontend | Next.js pages + API integration | 40 hrs |
| **Total** | | **~114 hrs (~8 weeks at 15 hrs/week)** |

## Upgrade Path

| Trigger | Action |
|---------|--------|
| Supabase free tier exceeded (unlikely for 5+ years) | Upgrade to Supabase Pro ($25/mo) or switch to any managed Postgres |
| Need custom domain on Vercel | Upgrade to Vercel Pro ($20/mo) |
| Need lower latency | Already on Fly.io Hong Kong |
| Need CSV import (Phase 2) | Python + pandas is ideal for this |
| Scale to 10+ parking lots | Same stack handles it, may need Supabase Pro for DB size |

## Open Questions

- **Monorepo vs dual-repo**: Keep frontend and backend in one repo (simpler CI) or separate (cleaner boundaries)?
- **CORS config**: FastAPI middleware for cross-origin requests from Vercel domain
- **Environment management**: `.env` files for local, Fly.io secrets for production
- **OpenAPI codegen**: Generate TypeScript client from FastAPI's auto-generated OpenAPI spec?
