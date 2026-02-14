# US-SEC-005: Row Level Security (RLS) Enforcement

> **Status: DROPPED from MVP** — Access control handled entirely in FastAPI auth middleware. Single DB user connection makes RLS redundant. Revisit if public-facing API added in Phase 2.

**Priority**: ~~Must Have~~ Dropped
**Phase**: ~~Phase 1~~ Deferred to Phase 2
**Domain**: Security & Authentication
**Epic**: Data Security
**Sprint**: Sprint 4 (Weeks 7-8)

## User Story

As a system administrator,
I want all database tables to enforce Row Level Security (RLS) policies,
So that data access is controlled at the database level even if application logic fails.

## Acceptance Criteria

- **AC1**: All 12 core tables (customers, spaces, agreements, payments, tags, waiting_list, system_logs, sites, etc.) have RLS enabled in Supabase
- **AC2**: RLS policy for admin role: SELECT, INSERT, UPDATE, DELETE allowed on all tables
- **AC3**: RLS policy for anonymous role: SELECT allowed only on spaces table (availability query) with restrictions:
  - Can only view space availability status (not customer/agreement details)
  - Cannot access customers, agreements, payments, system_logs tables
- **AC4**: RLS policy for system_logs table: Admin can SELECT only (no UPDATE/DELETE to preserve audit integrity)
- **AC5**: Given an attacker bypasses application logic, when they attempt direct database query, then RLS policies block unauthorized data access
- **AC6**: System performance: RLS policies do not degrade query performance by >10%

## Business Rules

- Defense in Depth: RLS provides database-level security layer in addition to API/UI access control
- Immutable Audit Logs: system_logs table prevents UPDATE/DELETE even for admins
- Future-Proofing: RLS policies support Phase 2 customer portal (self-service access to own data)

## Verification Method

- **Supabase Dashboard**: Verify RLS enabled on all tables
- **Policy Testing**: Attempt unauthorized queries via SQL editor with different roles
- **Performance Testing**: Benchmark query performance with RLS enabled vs. disabled
- **Security Audit**: Penetration testing with direct database access attempts

## Source

- init_draft.md lines 127-128
- CLAUDE.md security section

## Dependencies

- US-SEC-001 (authentication with roles)
- Database schema implementation

## Test Data

- Admin query: `SELECT * FROM customers` → Allowed
- Anonymous query: `SELECT * FROM customers` → Blocked by RLS
- Anonymous query: `SELECT id, status FROM spaces` → Allowed (availability only)
- Admin update: `UPDATE system_logs SET ...` → Blocked (immutable logs)
