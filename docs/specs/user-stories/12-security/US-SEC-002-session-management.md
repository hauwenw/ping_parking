# US-SEC-002: Session Management and Auto-Logout

**Priority**: Must Have
**Phase**: Phase 1
**Domain**: Security & Authentication
**Epic**: Authentication & Authorization
**Sprint**: Sprint 1 (Weeks 1-2)

## User Story

As a parking lot admin,
I want my session to persist securely across page refreshes and expire after inactivity,
So that my data remains accessible during work but secured when I'm away.

## Acceptance Criteria

- **AC1**: Given a logged-in admin, when they refresh the page or navigate between routes, then session persists without requiring re-login
- **AC2**: Given 24 hours of inactivity, when session expires, then system auto-logs out admin and redirects to login with message: "您的登入已過期，請重新登入"
- **AC3**: Given an admin with "Remember Me" enabled, when 7 days pass, then session expires and admin must re-login
- **AC4**: Given a logged-in admin, when they click "登出" (Logout) button, then system clears JWT token, invalidates session, logs logout action, and redirects to login page
- **AC5**: Given an active session, when JWT token is about to expire (within 5 minutes), then system automatically refreshes the token without user interaction
- **AC6**: System logs session expiration to system_logs (action=SESSION_EXPIRED, user_id, reason=inactivity|manual_logout|token_expired)

## Business Rules

- Session timeout: 24 hours of inactivity (user can extend with "Remember Me")
- Token refresh: Automatic silent refresh 5 minutes before expiration
- Concurrent sessions: Allowed. Each family member should have their own admin account (created via Supabase Auth dashboard) for better audit trail accountability. Multiple devices/sessions per account are permitted.
- Activity tracking: Any API call or page navigation resets inactivity timer

## UI Requirements

- **Screen**: All authenticated pages
- **Header**: "登出" (Logout) button in top-right corner of navigation bar
- **Session Expiry Modal**: Shows warning 2 minutes before expiration with "延長" (Extend) button
- **Auto-Logout Message**: Toast notification on logout: "您已成功登出"

## Source

- init_draft.md line 130

## Dependencies

- US-SEC-001 (authentication)

## Test Data

- Admin session: admin@ping.tw logged in for 23 hours 55 minutes → Token refresh triggered
- Expired session: admin@ping.tw idle for 24 hours → Auto-logout
- Manual logout: admin@ping.tw clicks logout → Session cleared
