# US-AGREE-007: Create Daily, Quarterly, and Yearly Agreements

**Priority**: Must Have | **Phase**: Phase 1 | **Sprint**: Sprint 4 (Weeks 7-8)
**Domain**: Agreement Management | **Epic**: Agreement Types

## User Story
As a parking lot admin, I want to create agreements for daily, quarterly, and yearly rentals (in addition to monthly), so that I can support different customer rental needs.

## Acceptance Criteria
- **AC1**: Agreement form supports 4 types: 日租 (Daily), 月租 (Monthly), 季租 (Quarterly), 年租 (Yearly)
- **AC2**: Daily → end_date = start + 1 day (2026-02-01 → 2026-02-02), rental period: "1 天"
- **AC3**: Quarterly → end_date = start + 3 months (2026-02-01 → 2026-05-01), rental period: "3 個月 (約 90 天)"
- **AC4**: Yearly → end_date = start + 1 year (2026-02-01 → 2027-02-01), rental period: "1 年 (約 365 天)"
- **AC5**: All types require at least one license plate, can have multiple (same validation as US-AGREE-003)
- **AC6**: All types follow same business rules: date range validation, auto-generate payment, validate availability, log
- **AC7**: **Future Enhancement (Phase 2/3)**: Allow custom end_date override for all agreement types (see US-AGREE-002)
- **AC8**: Agreement list shows type badge: 日(yellow)/月(blue)/季(purple)/年(green)

## Business Rules
- Same core logic for all types
- Only end date calculation differs (daily: +1d, quarterly: +3mo, yearly: +1yr)
- Pricing can vary by type
- License plates: At least one required for all types, can have multiple (see US-AGREE-003)
- Custom end dates: Phase 1 auto-calculates only. Future enhancement will allow override (see US-AGREE-002)

## UI Requirements
Type selection: Radio buttons with icons 📅日租/📆月租/🗓️季租/🗂️年租 | Default: 月租 | Dynamic end date display

## Source
init_draft.md lines 26, 67 | CLAUDE.md agreement types

## Dependencies
US-AGREE-001, US-AGREE-002, US-AGREE-003, US-AGREE-004

## Test Data
Daily: 2026-02-01 → 2026-02-02 (1天) | Quarterly: 2026-02-01 → 2026-05-01 (3個月) | Yearly: 2026-02-01 → 2027-02-01 (1年)
