# US-SEC-006: License Plate Encryption and Masking

**Priority**: Must Have
**Phase**: Phase 1
**Domain**: Security & Authentication
**Epic**: Data Privacy & Compliance
**Sprint**: Sprint 4 (Weeks 7-8)

## User Story

As a system administrator,
I want license plates encrypted in transit and masked in public views,
So that we protect customer vehicle information from unauthorized access.

## Acceptance Criteria

- **AC1**: Given an agreement creation or update with license plate, when data is transmitted to Supabase, then HTTPS/TLS encrypts data in transit
- **AC2**: License plates stored in database as plain text (for search/filtering), but transmitted over encrypted connection
- **AC3**: Given an anonymous user views public availability page (future), when license plates would be displayed, then system shows masked format: "ABC-***4" (first 3 chars + last 1 char visible)
- **AC4**: Given an admin views agreement details, when license plate is displayed, then full plate shown (no masking for authorized users)
- **AC5**: CSV export of agreements for admin includes full license plates (not masked)
- **AC6**: API responses to admin clients include full license plates, anonymous clients receive masked plates

## Business Rules

- Encryption in Transit: All API requests use HTTPS/TLS (Supabase default)
- Storage: Plain text storage in database for operational search/filter (not end-to-end encrypted)
- Masking: Applied only for anonymous/public views (not for admin users)
- Phase 1 Scope: Since no public access to agreements in Phase 1, masking primarily for future-proofing

## UI Requirements

- **Admin Views**: Full license plate display (e.g., "ABC-1234")
- **Future Public Views**: Masked display (e.g., "ABC-***4")
- **Search**: Admins can search by full license plate

## Verification Method

- **Network Audit**: Verify all API requests use HTTPS (inspect browser developer tools)
- **Database Inspection**: Confirm license plates stored in plain text (operational requirement)
- **Masking Testing**: (Future) Test anonymous API endpoints return masked plates
- **Admin Testing**: Verify admin users see full license plates in all views

## Source

- init_draft.md line 129
- CLAUDE.md security section

## Dependencies

- US-AGREE-003 (license plate requirement)
- US-SEC-003 (role-based access)

## Test Data

- Agreement license plate: ABC-1234
  - Admin view: "ABC-1234" (full plate)
  - Anonymous view (future): "ABC-***4" (masked)
- HTTPS verification: All requests to Supabase API use https:// protocol
