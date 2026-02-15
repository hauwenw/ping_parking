# Ping Parking Management System

Web-based parking lot management for 3 sites (~100 spaces) in Pingtung City, Taiwan. Handles daily/monthly/quarterly/yearly rental agreements, customer management, payments, and audit logging.

## Tech Stack

- **Backend**: FastAPI (Python 3.11) + SQLAlchemy + Alembic
- **Frontend**: Next.js 14 (TypeScript) + Tailwind CSS + shadcn/ui
- **Database**: PostgreSQL (Supabase, DB-only)
- **Deployment**: Fly.io (backend) + Vercel (frontend)

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # Configure DATABASE_URL, JWT_SECRET_KEY, ENCRYPTION_KEY
PYTHONPATH=. alembic upgrade head          # Run migrations
python scripts/seed.py        # Seed demo data
uvicorn app.main:app --reload # http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local  # Set NEXT_PUBLIC_API_URL
npm run dev                        # http://localhost:3000
```

### Run Tests

```bash
cd backend
pytest                # 70 tests
```

## Project Structure

```
backend/
  app/
    api/          # FastAPI route handlers
    models/       # SQLAlchemy ORM models
    schemas/      # Pydantic request/response schemas
    services/     # Business logic layer
    utils/        # Auth, crypto, errors, pricing
  scripts/        # Seed data
  tests/          # Pytest suite
frontend/
  src/app/        # Next.js App Router pages
  src/components/ # shadcn/ui components
  src/lib/        # API client, types, formatters
docs/specs/       # PRD, user stories, milestone plan
```

## Features

- **Space Management**: 3 sites, tag-based categorization, three-tier pricing (Tag > Custom > Site)
- **Customer Management**: Search, detail pages, agreement history
- **Agreements**: Create/terminate, auto-calculate end dates, double-booking prevention
- **Payments**: Auto-generated on agreement creation, complete/void lifecycle
- **Audit Log**: All mutations logged with old/new values, CSV export
- **Security**: JWT auth, license plate encryption (Fernet), production secret validation

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `JWT_SECRET_KEY` | Yes (prod) | JWT signing secret |
| `ENCRYPTION_KEY` | Yes (prod) | Fernet key for license plate encryption |
| `CORS_ORIGINS` | No | Allowed origins (default: `http://localhost:3000`) |
| `DEBUG` | No | Enable debug mode (default: `false`) |

### Frontend (`frontend/.env.local`)

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | No | Backend URL (default: `http://localhost:8000`) |

## Deployment

```bash
# Backend (Fly.io)
cd backend
fly launch              # First time
fly secrets set JWT_SECRET_KEY=... ENCRYPTION_KEY=... DATABASE_URL=...
fly secrets set CORS_ORIGINS=https://your-frontend.vercel.app
fly deploy

# Frontend (Vercel)
# Set NEXT_PUBLIC_API_URL to your Fly.io URL in Vercel dashboard
```

## License

Private - Wu Family Operations
