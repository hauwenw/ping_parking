# MVP Scope — Phase 1

**Date**: 2026-02-13
**Target**: First launchable version of Ping Parking Management System

## MVP Summary

35 user stories across 7 domains (net: +1 agreement list, -1 payment list) covering the complete CRUD lifecycle for parking operations: manage sites/spaces/tags, onboard customers, create agreements, track payments, with audit logging, localization, and security.

## In Scope (Phase 1 MVP)

### 01-space — Parking Space Management (6 stories)

| ID | Story | Sprint |
|----|-------|--------|
| US-SPACE-001 | Site Configuration (CRUD) | Sprint 1 |
| US-SPACE-002 | Create/Edit/Delete Spaces | Sprint 1 |
| US-SPACE-003 | Pricing Model (Base + Tag + Custom) | Sprint 2 |
| US-SPACE-004 | Tag Management (CRUD) | Sprint 1 |
| US-SPACE-005 | Space List View (Table with Filters) | Sprint 2 |
| US-SPACE-006 | View Space Detail | Sprint 2 |

**Covers**: 3 sites, ~100 spaces, enforced naming (`{prefix}-01`), bulk creation, 4 status states (available/occupied/maintenance/reserved), tag system with optional pricing, three-tier pricing hierarchy.

### 02-customer — Customer Management (5 stories)

| ID | Story | Sprint |
|----|-------|--------|
| US-CUST-001 | Create Customer | Sprint 1 |
| US-CUST-002 | View Customer Detail | Sprint 1 |
| US-CUST-003 | Edit Customer | Sprint 1 |
| US-CUST-004 | Search & Filter Customers | Sprint 2 |
| US-CUST-005 | Link to Agreement (Cross-Nav) | Sprint 2 |

**Covers**: Name + phone composite unique, contact_phone field, no deletion (permanent records), cross-page navigation to agreements.

### 03-agreement — Agreement Management (9 stories)

| ID | Story | Sprint |
|----|-------|--------|
| US-AGREE-001 | Create Agreement | Sprint 3 |
| US-AGREE-002 | Auto-Calculate End Dates | Sprint 3 |
| US-AGREE-003 | Require License Plate | Sprint 3 |
| US-AGREE-004 | Prevent Double Booking | Sprint 3 |
| US-AGREE-005 | View Agreement Detail + Renewal | Sprint 3 |
| US-AGREE-006 | Agreement Status (Computed + Termination) | Sprint 3 |
| US-AGREE-007 | All Agreement Types (Daily/Monthly/Quarterly/Yearly) | Sprint 3 |
| US-AGREE-008 | Cross-Page Navigation | Sprint 4 |
| US-AGREE-009 | Agreement List View (with Payment Status) | Sprint 4 |

**Covers**: 4 agreement types, computed status from dates, manual termination, license plate requirement, renewal flow with pre-fill, double-booking prevention, cross-domain navigation, agreement list with payment summary cards and overdue indicators.

### 04-payment — Payment Management (2 stories)

| ID | Story | Sprint |
|----|-------|--------|
| US-PAY-001 | Payment Lifecycle (Auto-Generate, Edit, Void) | Sprint 3 |
| US-PAY-002 | Record Payment (Manual Completion) | Sprint 3 |

**Covers**: Auto-generated on agreement creation, manual recording with bank reference, auto-void on termination, editable amounts with audit trail. Payment list view merged into US-AGREE-009 (agreement list with payment status column).

### 06-system-audit — System Audit (3 stories)

| ID | Story | Sprint |
|----|-------|--------|
| US-AUDIT-001 | View Audit Log | Sprint 4 |
| US-AUDIT-002 | Auto-Log All Actions | Sprint 1 |
| US-AUDIT-003 | Export Audit Log | Sprint 4 |

**Covers**: Complete audit trail for all mutations, old/new values as JSONB, filterable log viewer, CSV export.

### 10-localization — Localization (4 stories)

| ID | Story | Sprint |
|----|-------|--------|
| US-LOC-001 | Traditional Chinese UI | Sprint 1 |
| US-LOC-002 | Taiwan Phone Format | Sprint 1 |
| US-LOC-003 | TWD Currency Format | Sprint 1 |
| US-LOC-004 | Taiwan Date Format | Sprint 1 |

**Covers**: All UI in Traditional Chinese, phone stored as `09XXXXXXXX` displayed as `09XX-XXX-XXX`, NT$ currency with comma separators, YYYY年MM月DD日 date format.

### 12-security — Security & Auth (6 stories)

| ID | Story | Sprint |
|----|-------|--------|
| US-SEC-001 | Admin Authentication | Sprint 1 |
| US-SEC-002 | Session Management | Sprint 1 |
| US-SEC-003 | Role-Based Access | Sprint 2 |
| US-SEC-004 | Privacy-Compliant Data | Sprint 2 |
| US-SEC-005 | RLS Enforcement | Sprint 1 |
| US-SEC-006 | License Plate Encryption | Sprint 2 |

**Covers**: Supabase Auth with JWT, per-person admin accounts, concurrent sessions allowed, RLS on all tables, no national ID storage, license plate masking.

## Out of Scope (Phase 2)

| Domain | Description | Reason |
|--------|-------------|--------|
| **05-waiting-list** | FIFO queue per site, manual allocation | Not critical for launch — can manage informally |
| **07-bulk-operations** | CSV import for 6 entity types | Manual entry sufficient for ~100 spaces at launch |
| **08-user-workflows** | Separate workflow documentation | Core workflows already embedded in domain stories |
| **09-ui-ux** | Separate UI stories | UI requirements already specified in each domain story |
| **11-reporting** | Occupancy dashboard, revenue reports, late payment reports | Can use payment list + space list as interim reporting |

## Sprint Plan Overview

| Sprint | Weeks | Focus | Story Count |
|--------|-------|-------|-------------|
| Sprint 1 | 1-2 | Foundation: Sites, spaces, tags, customers, auth, localization, audit framework | 14 |
| Sprint 2 | 3-4 | Enhanced views: Pricing model, space list, customer search, RBAC, privacy | 8 |
| Sprint 3 | 5-6 | Core business: Agreements, payments, status lifecycle | 8 |
| Sprint 4 | 7-8 | Polish: Agreement list, cross-nav, audit viewer, export | 5 |

## Key Architectural Decisions

1. **Computed status** — Agreement status (pending/active/expired) derived from dates; only `terminated` stored. No cron jobs.
2. **PostgreSQL arrays for tags** — `TEXT[]` type, not junction tables. Query with `@>` operator.
3. **Three-tier pricing** — Site base → Tag price → Custom override. Tag price wins when applied.
4. **One payment per agreement** — No partial payments in Phase 1. Auto-generated at agreement creation.
5. **No customer deletion** — Records permanent for audit trail. Soft operations only.
6. **Manual payment recording** — No payment gateway. Admin enters bank reference for reconciliation.

## Open Issues (from PRD review)

| # | Issue | Risk | Status |
|---|-------|------|--------|
| 7 | License plate validation too loose | LOW | Open |
| 8 | Audit log performance at scale | MEDIUM | Open |
| 9 | Missing error states for cross-navigation | LOW | Open |
| 10 | UI stories directory empty | MEDIUM | Deferred to Phase 2 |
| 13 | Minor Chinese terminology inconsistencies | LOW | Open |

See `docs/specs/prd-review-remaining-issues.md` for details.
