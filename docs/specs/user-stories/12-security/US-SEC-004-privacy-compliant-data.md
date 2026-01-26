# US-SEC-004: Privacy-Compliant Data Entry (No National ID Storage)

**Priority**: Must Have
**Phase**: Phase 1
**Domain**: Security & Authentication
**Epic**: Data Privacy & Compliance
**Sprint**: Sprint 2 (Weeks 3-4)

## User Story

As a system administrator,
I want to ensure the system never stores national ID numbers,
So that we comply with Taiwan privacy regulations and protect customer privacy.

## Acceptance Criteria

- **AC1**: Database schema does NOT include national_id or similar fields in customers table or any other table
- **AC2**: Customer creation forms do NOT display national ID input fields
- **AC3**: CSV import templates do NOT include national_id columns
- **AC4**: System documentation explicitly states "No national ID storage per privacy policy"
- **AC5**: Given a developer attempts to add national_id field to database, when database migration runs, then code review process rejects it

## Business Rules

- Privacy Compliance: Taiwan Personal Data Protection Act (PDPA) compliance
- Customer Identification: Use phone number + name + email (no national ID)
- Data Minimization: Only collect data necessary for parking lot operations

## Verification Method

- **Database Audit**: Review all database schemas and confirm no national_id fields
- **Code Review**: Scan all form components for national_id inputs
- **CSV Template Review**: Verify all 6 CSV templates exclude national_id columns
- **Documentation Review**: Confirm privacy policy documented in init_draft.md and CLAUDE.md

## Source

- init_draft.md line 126

## Related Stories

- US-CUST-001 (customer registration)
- US-BULK-001 (CSV import customers)
