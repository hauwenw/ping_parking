# US-SEC-003: Role-Based Access Control (Admin-Only Phase 1)

**Priority**: Must Have
**Phase**: Phase 1
**Domain**: Security & Authentication
**Epic**: Authentication & Authorization
**Sprint**: Sprint 1 (Weeks 1-2)

## User Story

As a system administrator,
I want to ensure only admins can access parking lot management features,
So that public users cannot modify critical business data.

## Acceptance Criteria

- **AC1**: Given an unauthenticated user, when they attempt to access any route except `/login` or `/availability` (public), then system redirects to login page
- **AC2**: Given an authenticated admin, when they access any protected route, then system verifies user role is "admin" before rendering the page
- **AC3**: Given an anonymous user, when they access `/availability` route, then system allows read-only access to space availability data (no customer/payment info visible)
- **AC4**: System validates user role on every API request to protected endpoints (not just UI routing)
- **AC5**: Given an admin token expires or is invalidated, when they attempt any action, then system immediately redirects to login with message: "請重新登入以繼續"

## Business Rules

- Phase 1 roles: "admin" (full access) and "anonymous" (public availability only)
- Admin routes: All pages under `/admin/*` (dashboard, customers, agreements, etc.)
- Public routes: `/login`, `/availability` (future customer self-service portal)
- API endpoints: All mutations (create/update/delete) require admin role
- RLS policies: Supabase Row Level Security enforces role checks at database level

## UI Requirements

- **Protected Routes**: All management pages require admin role
- **Public Routes**: Availability page styled as read-only (no action buttons)
- **Unauthorized Access**: Show 403 error page in Traditional Chinese: "您沒有權限訪問此頁面"

## Source

- init_draft.md lines 33-37, 134

## Dependencies

- US-SEC-001 (authentication)
- US-SEC-002 (session management)

## Test Data

- Admin user: admin@ping.tw → Full access to all routes
- Anonymous user: No login → Can only view `/availability`
- Expired admin token: Expired JWT → Redirect to login
