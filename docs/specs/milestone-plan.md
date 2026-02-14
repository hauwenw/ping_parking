# Milestone Plan — Ping Parking MVP

**Date**: 2026-02-14
**Tech Stack**: FastAPI + Supabase (DB-only) + Next.js + Fly.io
**Total**: 34 stories, ~116 hours, ~8 weeks at 15 hrs/week

## Context

The Ping Parking Management System has 34 user stories across 7 domains. This plan structures the work into **6 milestones** with clear deliverables, following the dependency chain and enabling backend/frontend parallelization where possible.

The key architectural decision: **separate backend (FastAPI) and frontend (Next.js)** means we need an upfront "Milestone 0" for scaffolding and API contract definition, and we can work backend and frontend in parallel within a milestone once API contracts are defined.

## Dependency Chain (Critical Path)

```
SEC-001 (auth) → AUDIT-002 (logging) → SPACE-001 (sites) → SPACE-002 (spaces)
  → SPACE-003 (pricing) → AGREE-001 (agreements) → PAY-001 (payments) → AGREE-009 (list)
```

Other chains:
- **Customer**: CUST-001 → CUST-005 → AGREE-008
- **Security**: SEC-001 → SEC-006 → AGREE-003
- **Tags**: SPACE-004 → SPACE-003 → AGREE-001

---

## Milestone 0: Project Scaffolding & Infrastructure (Week 1)

**Goal**: Both repos buildable, deployable, and connected to Supabase. No business logic yet.

### Backend Deliverables
- [ ] FastAPI project structure (`app/`, `alembic/`, `tests/`, `Dockerfile`)
- [ ] Supabase PostgreSQL connection (session mode, port 5432)
- [ ] Alembic configured and first empty migration runs
- [ ] Docker image builds and runs locally
- [ ] Health check endpoint (`GET /health`)
- [ ] pytest + testcontainers setup (one smoke test)
- [ ] Fly.io deploy pipeline (fly.toml, GitHub Actions or manual `flyctl deploy`)

### Frontend Deliverables
- [ ] Next.js 14 project with TypeScript, Tailwind CSS, shadcn/ui
- [ ] API client module (typed HTTP client pointing to backend URL)
- [ ] Basic layout shell: sidebar nav (5 menu items), header, content area
- [ ] Login page UI (form only, no auth logic yet)
- [ ] Vercel deployment (or local dev only)

### Infrastructure Deliverables
- [ ] Supabase project created, connection string stored in Fly.io secrets
- [ ] CORS middleware configured in FastAPI (allow Vercel domain)
- [ ] Environment variable management (`.env.example` for local, secrets for prod)

**Exit Criteria**: `flyctl deploy` succeeds, frontend loads shell layout, backend health check returns 200 from Fly.io Hong Kong.

**Estimated Effort**: ~8 hours

---

## Milestone 1: Foundation — Auth, Audit, Sites, Spaces, Tags, Customers (Weeks 2-3)

**Goal**: Admin can log in, create sites/spaces/tags/customers. All mutations are audit-logged.

### Stories (14 total)

| ID | Story | Layer |
|----|-------|-------|
| US-SEC-001 | Admin Authentication (JWT) | Backend + Frontend |
| US-SEC-002 | Session Management (24hr timeout, remember me) | Backend + Frontend |
| US-SEC-003 | Role-Based Access (admin-only middleware) | Backend |
| US-AUDIT-002 | Auto-Log All Admin Actions | Backend |
| US-LOC-001 | Traditional Chinese UI | Frontend |
| US-LOC-002 | Taiwan Phone Format (09XX-XXX-XXX) | Backend + Frontend |
| US-LOC-003 | TWD Currency Format (NT$1,234) | Frontend |
| US-LOC-004 | Taiwan Date Format (YYYY年MM月DD日) | Frontend |
| US-SPACE-001 | Site Configuration CRUD | Backend + Frontend |
| US-SPACE-002 | Create/Edit/Delete Spaces | Backend + Frontend |
| US-SPACE-004 | Tag Management CRUD | Backend + Frontend |
| US-CUST-001 | Create Customer | Backend + Frontend |
| US-CUST-002 | View Customer Detail | Backend + Frontend |
| US-CUST-003 | Edit Customer | Backend + Frontend |

### Backend Deliverables
- [ ] **Database**: Alembic migrations for `sites`, `spaces`, `tags`, `customers`, `system_logs` tables
- [ ] **Auth**: JWT login/logout endpoints, auth middleware, admin_users seed
- [ ] **Audit**: `AuditLogger` service, integrated into all CRUD services
- [ ] **APIs**: Full CRUD for sites, spaces, tags, customers (16+ endpoints)
- [ ] **Validation**: Phone format (09XXXXXXXX), email format, required fields
- [ ] **Tests**: Integration tests for auth flow, customer CRUD, audit logging

### Frontend Deliverables
- [ ] Login page with JWT token flow (store in httpOnly cookie or memory)
- [ ] Protected route wrapper (redirect to /login if no token)
- [ ] Sidebar navigation (Traditional Chinese labels)
- [ ] Site management page (CRUD modal forms)
- [ ] Space management page (table view, create/edit modals)
- [ ] Tag management page (color picker, CRUD)
- [ ] Customer management page (create/edit forms, detail view)
- [ ] Formatters: phone display, currency display, date display

**Exit Criteria**: Admin logs in, creates a site with spaces and tags, creates a customer. All actions appear in system_logs table.

**Estimated Effort**: ~30 hours

---

## Milestone 2: Enhanced Views — Pricing, Search, Privacy (Weeks 4-5)

**Goal**: Three-tier pricing works, space/customer list views have filters, license plates are encrypted.

### Stories (7 total)

| ID | Story | Layer |
|----|-------|-------|
| US-SPACE-003 | Pricing Model (Site base + Tag + Custom) | Backend + Frontend |
| US-SPACE-005 | Space List View (Table with Tag/Status Filters) | Backend + Frontend |
| US-SPACE-006 | View Space Detail | Backend + Frontend |
| US-CUST-004 | Search & Filter Customers | Backend + Frontend |
| US-CUST-005 | Link to Agreement (Cross-Nav Setup) | Frontend |
| US-SEC-004 | Privacy-Compliant Data (no national ID) | Backend (enforcement) |
| US-SEC-006 | License Plate Encryption | Backend |

**Note**: US-SEC-005 (RLS) dropped — access control handled entirely in FastAPI middleware since we connect as a single DB user. Revisit if public API added in Phase 2.

### Backend Deliverables
- [ ] **Pricing**: Three-tier calculation function (site base -> tag price -> custom override)
- [ ] **Space API**: List with filters (site, tag, status), pagination
- [ ] **Customer API**: Search by name/phone, filter, pagination
- [ ] **License Plate**: Encryption/decryption utility for storage
- [ ] **Privacy**: Validation rules ensuring no national ID fields accepted

### Frontend Deliverables
- [ ] Space list page: table with sticky header, tag filter chips, status filter
- [ ] Space detail page: pricing breakdown, tag dots, current agreement info
- [ ] Customer list page: search bar, phone filter, active agreement count column
- [ ] Customer detail page: link to future agreements section (placeholder)
- [ ] Pricing display: show computed price with tier breakdown

**Exit Criteria**: Admin can filter spaces by tag, see pricing hierarchy, search customers by phone. License plates encrypted in DB.

**Estimated Effort**: ~20 hours

---

## Milestone 3: Core Business — Agreements & Payments (Weeks 5-6)

**Goal**: Admin can create monthly agreements, payments auto-generate, double-booking prevented.

### Stories (8 total)

| ID | Story | Layer |
|----|-------|-------|
| US-AGREE-001 | Create Monthly Rental Agreement | Backend + Frontend |
| US-AGREE-002 | Auto-Calculate End Dates | Backend |
| US-AGREE-003 | Require License Plate for All Types | Backend + Frontend |
| US-AGREE-004 | Prevent Double-Booking | Backend (app-level check) |
| US-AGREE-005 | View Agreement Details | Backend + Frontend |
| US-AGREE-006 | Agreement Status (Computed + Termination) | Backend |
| US-PAY-001 | Payment Lifecycle (Auto-Generate, Edit, Void) | Backend + Frontend |
| US-PAY-002 | Record Payment (Manual Completion) | Backend + Frontend |

### Backend Deliverables
- [ ] **Database**: Alembic migrations for `agreements`, `payments` tables
- [ ] **Computed View**: `agreements_with_status` (pending/active/expired/terminated)
- [ ] **End Date Calc**: `calculate_end_date()` function (daily/monthly/quarterly/yearly)
- [ ] **Double-Booking**: Overlap check in agreement service (app-level, not DB trigger)
- [ ] **Payment Auto-Gen**: Create payment record when agreement is created
- [ ] **Termination**: Terminate agreement endpoint (void pending payments)
- [ ] **APIs**: Agreement CRUD + payment recording endpoints
- [ ] **Editability**: Notes and license_plates always editable, other fields immutable
- [ ] **Tests**: Double-booking prevention, payment auto-generation, status computation

### Frontend Deliverables
- [ ] Agreement creation form: customer picker, space picker, date picker, license plate input
- [ ] Agreement detail page: status badge, termination button with reason modal
- [ ] Payment section: auto-generated payment card, record payment modal (bank ref, date)
- [ ] Inline price display from space pricing hierarchy

**Exit Criteria**: Admin creates monthly agreement for customer+space, payment auto-generates, cannot double-book same space, can terminate and record payment.

**Estimated Effort**: ~28 hours

---

## Milestone 4: Polish — Agreement List, All Types, Cross-Nav, Audit UI (Weeks 7-8)

**Goal**: Agreement list is the landing page with payment status. All 4 agreement types work. Cross-page navigation complete.

### Stories (5 total)

| ID | Story | Layer |
|----|-------|-------|
| US-AGREE-007 | Create Daily/Quarterly/Yearly Agreements | Backend + Frontend |
| US-AGREE-008 | Cross-Page Navigation | Frontend |
| US-AGREE-009 | Agreement List View (with Payment Status) | Backend + Frontend |
| US-AUDIT-001 | View System Audit Log | Backend + Frontend |
| US-AUDIT-003 | Export Audit Log to CSV | Backend + Frontend |

### Backend Deliverables
- [ ] **All Types**: Extend agreement creation for daily/quarterly/yearly (end date calc already handles this)
- [ ] **Agreement List API**: Paginated list with payment status join, filters (status, type, site)
- [ ] **Audit Log API**: Paginated, filterable (date range, user, action, table)
- [ ] **Audit Export**: CSV download endpoint with same filters
- [ ] **Tests**: All agreement types, audit log pagination

### Frontend Deliverables
- [ ] **Agreement list page** (default landing after login): table with columns for customer, space, type, status, payment status, dates
- [ ] Payment status badges (paid/pending/overdue) in agreement list
- [ ] Agreement type selector in creation form (daily/monthly/quarterly/yearly)
- [ ] **Cross-page navigation**: Customer -> Agreements, Agreement -> Customer, Agreement -> Payment, Space -> Agreement
- [ ] Audit log viewer page: table with filters, detail modal (JSON diff), pagination
- [ ] Audit log CSV export button

**Exit Criteria**: Admin logs in, sees agreement list with payment status. Can navigate between customer/agreement/payment. Can view and export audit logs. All 4 agreement types work.

**Estimated Effort**: ~22 hours

---

## Milestone 5: Integration Testing & Launch Prep (Week 8+)

**Goal**: End-to-end testing, bug fixes, deployment hardening.

### Deliverables
- [ ] End-to-end smoke test: full workflow (login -> create customer -> create space -> create agreement -> record payment -> view audit log)
- [ ] Cross-browser testing (Chrome, Safari on desktop + tablet)
- [ ] Performance check: audit log query with 1000+ rows
- [ ] Error handling review: all API errors return Traditional Chinese messages
- [ ] Fly.io production config: `min_machines_running=1`, Hong Kong region verified
- [ ] Supabase free tier usage check (DB size, bandwidth)
- [ ] Seed data: test accounts (admin1@ping.tw, admin2@ping.tw)
- [ ] Documentation: deployment runbook, admin user guide (brief)

**Exit Criteria**: Wu family can log in and manage parking operations end-to-end.

**Estimated Effort**: ~8 hours

---

## Summary Timeline

| Milestone | Focus | Stories | Effort | Cumulative |
|-----------|-------|---------|--------|------------|
| **M0** | Scaffolding & Infra | 0 | ~8 hrs | Week 1 |
| **M1** | Auth, Audit, Sites, Spaces, Tags, Customers | 14 | ~30 hrs | Weeks 2-3 |
| **M2** | Pricing, Search, Privacy | 7 | ~20 hrs | Weeks 4-5 |
| **M3** | Agreements & Payments | 8 | ~28 hrs | Weeks 5-6 |
| **M4** | Agreement List, All Types, Cross-Nav, Audit UI | 5 | ~22 hrs | Weeks 7-8 |
| **M5** | Integration Testing & Launch | 0 | ~8 hrs | Week 8+ |
| **Total** | | **34** | **~116 hrs** | **~8 weeks** |

---

## Decisions Made

- **RLS dropped (SEC-005)**: Access control handled entirely in FastAPI auth middleware. Single DB user connection makes RLS redundant. Revisit only if public-facing API added in Phase 2.
- **Double-booking**: Implement in application layer (FastAPI service), not as DB trigger. Easier to test and debug in Python.
- **Audit logging**: Application-layer `AuditLogger` service, not database triggers. Consistent with "business logic in app code" decision.

## Key Files Referenced

- `docs/specs/mvp-scope.md` — Sprint plan and story assignments
- `docs/specs/tech-stack-plan.md` — Chosen tech stack and cost breakdown
- `docs/specs/user-stories/03-agreement/README.md` — Agreement schema, computed status, double-booking trigger
- `docs/specs/user-stories/06-system-audit/README.md` — System logs schema, immutability enforcement
- `docs/specs/user-stories/12-security/US-SEC-001-admin-authentication.md` — Login flow and redirect
- `CLAUDE.md` — Architecture overview, business rules, navigation hierarchy
