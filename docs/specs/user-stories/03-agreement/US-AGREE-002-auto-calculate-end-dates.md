# US-AGREE-002: Auto-Calculate Agreement End Dates

**Priority**: Must Have | **Phase**: Phase 1 | **Sprint**: Sprint 3 (Weeks 5-6)
**Domain**: Agreement Management | **Epic**: Agreement Lifecycle

## User Story
As a parking lot admin, I want the system to automatically calculate end dates based on agreement type and start date, so that I don't have to manually calculate expiration dates.

## Acceptance Criteria
- **AC1**: Daily → start_date + 1 day (2026-02-01 → 2026-02-02)
- **AC2**: Monthly → start_date + 1 month (2026-02-01 → 2026-03-01, 2026-01-31 → 2026-02-28)
- **AC3**: Quarterly → start_date + 3 months (2026-02-01 → 2026-05-01)
- **AC4**: Yearly → start_date + 1 year (2026-02-01 → 2027-02-01, 2024-02-29 → 2025-02-28)
- **AC5**: Calculation server-side (DB function or API)
- **AC6**: End date read-only in UI (cannot manually edit)
- **AC7**: Agreement detail shows rental duration: "1 個月 (28 天)"
- **AC8**: Daily batch job (cron) handles automatic status transitions:
  - `pending` agreements: if current_date >= start_date → status="active"
  - `active` agreements: if current_date > end_date → status="expired"
- **AC9**: **Future Enhancement (Phase 2/3)**: Allow admin to override calculated end_date with custom date for non-standard agreements (e.g., partial month rentals, special promotions)

## Business Rules
- **Server-Side Calculation**: Ensures consistency across all clients
- **Immutable End Date (Phase 1)**: Cannot change after creation (must terminate and recreate)
- **Edge Cases**: Use PostgreSQL interval addition (not simple +30 days) to handle month-end correctly
- **Date-Only Fields**: No time component (midnight UTC assumed)
- **Automatic Status Transitions**: Cron job runs daily at midnight Taiwan time (see US-AGREE-006)
- **Custom End Dates (Future Enhancement)**: Phase 1 always auto-calculates. Future phases will allow manual override for special cases (e.g., partial month rentals, corporate contracts, promotional rates)

## Implementation Notes
```sql
-- PostgreSQL interval addition
UPDATE agreements SET end_date = start_date + INTERVAL '1 month'  -- Handles Jan 31 → Feb 28/29
UPDATE agreements SET end_date = start_date + INTERVAL '1 year'   -- Handles leap years
```

## UI Requirements
End date field grayed out, shows calculated value | Agreement detail displays breakdown: 開始日期/結束日期/租期

## Source
init_draft.md line 67 | CLAUDE.md agreement lifecycle

## Dependencies
US-AGREE-001, US-LOC-004

## Test Data
Daily: 2026-02-01 → 2026-02-02 | Monthly: 2026-01-31 → 2026-02-28 (edge) | Quarterly: 2026-11-30 → 2027-02-28 | Yearly: 2024-02-29 → 2025-02-28 (leap year)
