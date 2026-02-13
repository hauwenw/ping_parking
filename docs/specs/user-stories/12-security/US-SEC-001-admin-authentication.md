# US-SEC-001: Admin Authentication with Supabase Auth

**Priority**: Must Have
**Phase**: Phase 1
**Domain**: Security & Authentication
**Epic**: Authentication & Authorization
**Sprint**: Sprint 1 (Weeks 1-2)

## User Story

As a parking lot admin,
I want to securely log in to the system using Supabase Auth,
So that only authorized users can access and manage parking lot data.

## Acceptance Criteria

- **AC1**: Given an admin user with valid credentials, when they submit the login form with email and password, then Supabase Auth validates credentials and issues a JWT token
- **AC2**: Given a successful login, when the JWT token is issued, then the system stores the token securely in HttpOnly cookies (not localStorage)
- **AC3**: Given an invalid email or password, when admin submits login form, then system shows error in Traditional Chinese: "電子郵件或密碼錯誤，請重試"
- **AC4**: Given a logged-in admin, when they navigate to any protected route, then system validates JWT token before allowing access
- **AC5**: System logs successful login to system_logs (action=LOGIN, user_id, ip_address, timestamp)
- **AC6**: System logs failed login attempts to system_logs (action=FAILED_LOGIN, attempted_email, ip_address, timestamp)

## Business Rules

- Admin accounts created via Supabase Auth dashboard (no self-registration). Each family member should have their own account for audit trail accountability.
- Minimum password strength: 8 characters, mix of letters and numbers
- Session timeout: 24 hours of inactivity
- Failed login lockout: 5 failed attempts = 15-minute account lockout

## UI Requirements

- **Screen**: Login page (route: `/login`)
- **Form Fields**:
  - Email (text input, required, email validation)
  - Password (password input, required, show/hide toggle)
  - "記住我" (Remember me) checkbox (extends session to 7 days)
  - "登入" (Login) button (primary CTA)
- **Validation**: Inline validation with Traditional Chinese error messages
- **Loading State**: Button shows loading spinner during authentication
- **Success**: Redirect to dashboard (儀表板) on successful login

## Source

- init_draft.md lines 53, 130

## Dependencies

- Supabase Auth setup

## Test Data

- Valid admin 1: admin1@ping.tw / Password123 (e.g., family member A)
- Valid admin 2: admin2@ping.tw / Password456 (e.g., family member B)
- Both logged in simultaneously on different devices → Both sessions active
- Invalid email: invalid@example.com / Password123 → Error
- Invalid password: admin1@ping.tw / WrongPass → Error
