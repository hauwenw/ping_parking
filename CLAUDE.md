# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Ping Parking Management System - A web-based platform for managing Wu family parking operations in Pingtung City, Taiwan. Manages 3 parking lots with ~100 spaces supporting daily, monthly, quarterly, and yearly rental agreements.

**Tech Stack**: FastAPI (Python) + Supabase (DB-only PostgreSQL) + Next.js 14 (TypeScript) + Tailwind CSS + shadcn/ui

**Language**: Traditional Chinese (Taiwan) with TWD currency formatting

## Development Commands

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload    # Start dev server at http://localhost:8000
pytest                           # Run test suite
alembic upgrade head             # Run database migrations
alembic revision --autogenerate -m "description"  # Create migration
```

### Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev              # Start development server at http://localhost:3000
npm run build            # Production build
npm run lint             # Run ESLint
npm run type-check       # TypeScript type checking
npm test                 # Run test suite
npm test -- <file>       # Run single test file
```

### Database (Supabase — DB-only)
```bash
# Connection via DATABASE_URL environment variable
# Migrations managed by Alembic (see Backend commands above)
```

## Documentation and Technical References

When you need to check technical specifications, API documentation, or implementation details for the tech stack:

**Use context7 MCP server** for up-to-date documentation:
- Next.js 14 features and APIs
- Supabase client libraries and database operations
- Tailwind CSS utilities and configuration
- shadcn/ui component APIs
- TypeScript best practices

This ensures you're working with current, accurate technical specifications rather than relying on potentially outdated information.

## Key Project Documentation

### Planning & Architecture
- `docs/specs/tech-stack-plan.md` — Tech stack decision, architecture diagram, project structure, cost breakdown
- `docs/specs/milestone-plan.md` — 6-milestone implementation plan (M0-M5), 34 stories, ~116 hours
- `docs/specs/mvp-scope.md` — MVP scope definition, story assignments, sprint plan

### Coding Conventions
- `docs/specs/coding-conventions-python.md` — Python/FastAPI backend: project structure, naming, Pydantic schemas, SQLAlchemy models, service layer, error handling, testing
- `docs/specs/coding-conventions-frontend.md` — JS/Next.js frontend: App Router structure, TypeScript, components, data fetching, Tailwind styling, forms, localization

### User Stories by Domain
- `docs/specs/user-stories/README.md` — User stories index (all 34 stories)
- `docs/specs/user-stories/01-space/README.md` — Space Management (SPACE-001 to SPACE-006)
- `docs/specs/user-stories/02-customer/README.md` — Customer Management (CUST-001 to CUST-005)
- `docs/specs/user-stories/03-agreement/README.md` — Agreement Management (AGREE-001 to AGREE-009)
- `docs/specs/user-stories/04-payment/README.md` — Payment Management (PAY-001 to PAY-003)
- `docs/specs/user-stories/06-system-audit/README.md` — System Audit (AUDIT-001 to AUDIT-003)
- `docs/specs/user-stories/10-localization/README.md` — Localization (LOC-001 to LOC-004)
- `docs/specs/user-stories/12-security/README.md` — Security (SEC-001 to SEC-006)

### Original Specification
- `init_draft.md` — Complete product specification, workflows, UI mockups

## Architecture Overview

### Database Schema (12 Core Tables)

**Primary Entities**:
- `customers` - Customer records with name, phone, contact_phone, email (NO national ID for privacy). Unique constraint on (name, phone).
- `spaces` - Parking spaces with site_id, name, tags[] (array), status, custom_price
- `agreements` - Rental contracts linking customer + space + license_plate with agreement_type (daily/monthly/quarterly/yearly)
- `payments` - Payment records linked to agreements with bank references
- `tags` - Flexible tag system with name, color, description (replaces fixed categories)
- `system_logs` - Complete audit trail of all admin actions with old_values/new_values JSON

**Key Relationships**:
- Customer → Agreements (1:N) → Payments (1:1 per agreement)
- Space → Agreement (1:1 when active)
- Tags → Spaces (M:N via array field)

**Important**:
- Each space can have ONLY ONE active agreement at a time
- Spaces use PostgreSQL array type for tags (e.g., `tags: ['有屋頂', 'VIP']`)
- Access control enforced in FastAPI auth middleware (no RLS — single DB user)

### Frontend Structure

**Navigation Hierarchy** (MVP):
1. 停車場管理 (Site/Space Management) - Table view with tag/status filters
2. 客戶管理 (Customer Management) - Customer list with active agreement counts
3. 合約管理 (Agreement Management) - Agreement list with payment status, cross-page navigation (**default landing page after login**)
4. 系統設定 (System Settings) - Tag configuration, site settings, admin settings
5. 系統紀錄 (Audit Log) - Activity log viewer with export

**Deferred to Phase 2**:
6. 儀表板 (Dashboard) - Tag stats, occupancy, alerts
7. 候補名單 (Waiting List) - Manual FIFO queues by site
8. 報表 (Reports) - Occupancy, revenue, late payments

**UI/UX Patterns**:
- Desktop-first responsive design optimized for tablet use
- Cross-page navigation between related entities (customer ↔ agreement ↔ payment)
- Color-coded tag dots on space grids for quick visual scanning
- Modal forms for create/edit operations
- Inline validation with Traditional Chinese error messages

### Tag System Architecture

Tags replace fixed categories with flexible, color-coded labels that support:
- Multiple tags per space (e.g., `['有屋頂', 'VIP', '大車位']`)
- Optional tag-based pricing (see Pricing Model below)
- Visual indicators via color dots on space grids
- Dynamic filtering and reporting by tag combinations

**Implementation**: Use PostgreSQL array type, NOT junction tables. Query with `@>` operator for tag filtering.

### Pricing Model

Three-tier pricing hierarchy (see US-SPACE-003):
1. **Site base price** - Default monthly/daily rates per site (e.g., Site A: monthly=3600, daily=150)
2. **Tag price** - Tags can optionally define prices; when added to space, space price updates to tag price
3. **Custom space price** - Admin can manually override price per space

**Priority**: Tag price > Custom price > Site base price

**Key behaviors**:
- Adding tag with price → Space price updates immediately
- Removing tag → Price stays (does NOT revert)
- Agreement price = immutable snapshot at creation time (space price changes don't affect existing agreements)

### CSV Import System

Supports 6 bulk import formats with validation:
1. Customers (name, phone, email, notes)
2. Spaces (site, name, tags)
3. Agreements (customer_phone, space_name, license_plate, dates)
4. Payments (agreement_ref, amount, date, bank_ref)
5. Tags (name, color, description)
6. Waiting List (customer_phone, site, priority)

**Workflow**: Template download → validation → progress tracking → import log review → retry failed records

### System Logging Architecture

All admin actions must be logged to `system_logs` with:
- `action` (CREATE/UPDATE/DELETE/IMPORT/etc)
- `table` and `record_id` for traceability
- `old_values` and `new_values` as JSONB for complete audit trail
- `user_id`, `ip_address`, `timestamp`

Implement using application-layer AuditLogger service in FastAPI, NOT client-side logging or database triggers.

## Critical Business Rules

### Space Allocation
1. Check space status before allocation
2. Verify no existing active agreement on space
3. Require license plate for ALL agreement types
4. Auto-generate payment record on agreement creation
5. Log all allocation actions to system_logs

### Agreement Lifecycle
- Start date + agreement_type determines end_date automatically
- Status computed from dates (pending/active/expired) or manually set (terminated)
- Cannot delete agreements with associated payments (soft delete only)
- End date calculation: monthly (+1mo), quarterly (+3mo), yearly (+1yr), daily (+1d)

### Payment Lifecycle (see US-PAY-001)
- **One payment per agreement**: Auto-generated at agreement creation with amount = agreement price
- **Payment amount**: Editable by admin with logged reason (e.g., discounts)
- **Termination impact**: Pending payments auto-voided when agreement is terminated; completed payments unchanged
- **No partial payments** in Phase 1: Full amount only
- **Status flow**: pending → completed / voided (no reactivation)

### Payment Processing
- Payments are recorded manually (no gateway in Phase 1)
- One payment record per agreement (not installments)
- Payment status: pending/completed/voided
- Payment date may differ from agreement start date
- Bank reference required for audit purposes

### Waiting List Management
- FIFO queue per site (NOT per space)
- Admin manually assigns spaces to waiting list customers
- No automatic allocation
- Remove from list after successful allocation

## Localization Requirements

All UI text, validation messages, and notifications must use Traditional Chinese:
- Phone format: Stored as `09XXXXXXXX` (no dashes), displayed as `09XX-XXX-XXX`
- Currency: `NT$1,234` (comma separators)
- Date format: `YYYY年MM月DD日` or ISO for forms
- Number format: Arabic numerals with Chinese units

## Security Considerations

1. **Privacy Compliance**: Never store national ID numbers
2. **Access Control**: FastAPI auth middleware on all endpoints (no RLS — single DB user)
3. **Authentication**: Self-managed JWT in FastAPI middleware (no Supabase Auth)
4. **Audit Trail**: Application-layer AuditLogger service for all write operations
5. **License Plate Privacy**: Encrypt in transit, mask in public views

## Testing Strategy

Focus testing on:
- Space allocation conflicts (double-booking prevention)
- Agreement date calculations across all types
- Tag filtering with array operators
- CSV import validation and error handling
- Cross-page navigation data integrity
- FastAPI auth middleware enforcement

## Common Pitfalls

1. **Do NOT use junction tables for tags** - Use PostgreSQL arrays
2. **Do NOT allow multiple active agreements per space** - Enforce at database level
3. **Do NOT skip system logging** - Required for all mutations
4. **Do NOT hardcode categories** - Everything must use the tag system
5. **Do NOT store sensitive data** - No national IDs, minimize PII

## Deployment Notes

- **Backend**: Fly.io Hong Kong region (Docker, $3-5/mo)
- **Frontend**: Vercel Free (Next.js)
- **Database**: Supabase free PostgreSQL (DB-only, no Auth/RLS/PostgREST)
- **Target Cost**: $4-6/month
- **Monitoring**: Vercel analytics + Supabase dashboard

## Project Status

MVP feature-complete (M0-M4). Backend: FastAPI with 70 tests, 6 domains (sites, tags, spaces, customers, agreements, payments), audit logging, JWT auth. Frontend: Next.js with 11 routes, CRUD pages, detail pages, cross-navigation. Remaining: M5 (deployment config, seed data, production testing).
