# US-AGREE-001: Create Monthly Rental Agreement

**Priority**: Must Have | **Phase**: Phase 1 | **Sprint**: Sprint 3 (Weeks 5-6)
**Domain**: Agreement Management | **Epic**: Agreement Lifecycle

## User Story
As a parking lot admin, I want to create a monthly rental agreement linking a customer, parking space, and license plate(s), so that I can formalize the rental contract and track occupancy.

## Acceptance Criteria
- **AC1**: start_date + "monthly" → end_date = start_date + 1 month (2026-02-01 → 2026-03-01)
- **AC2**: System validates: at least one license plate provided, customer exists, no date range overlap with existing agreements
- **AC3**: Date overlap check: Query agreements for same space WHERE status IN ('pending', 'active') AND (new_start, new_end) OVERLAPS (existing_start, existing_end) → Error: "此車位在選定日期已被分配 (YYYY-MM-DD 至 YYYY-MM-DD)"
- **AC4**: On creation, system atomically:
  - Sets `status = 'active'` (meaning "not terminated"). Display status (pending/active) is computed from dates per US-AGREE-006
  - Auto-generates payment record (amount, due_date=start_date, status="pending")
  - Space status remains computed (occupied only if non-terminated agreement covers current_date)
  - Logs to system_logs
- **AC5**: Missing license plate → Error: "至少需要一個車牌號碼"
- **AC6**: Success → Redirect to agreement detail page showing all info + payment link + status badge (進行中/待生效)

## Business Rules
- **Date Range Validation**: Space can have multiple agreements if date ranges don't overlap
- **License Plates**: At least one required, multiple allowed (stored as TEXT[] array). Admin can add/remove plates with "+ 新增車牌" button (see US-AGREE-003)
- **End Date**: start_date + 1 month, auto-calculated (see US-AGREE-002)
- **Initial Status**: Always `status='active'` (meaning "not terminated"). The display status (pending vs active) is computed from dates (see US-AGREE-006)
- **Payment Generation**: Created at agreement creation (not activation) with amount=agreement price, due_date=start_date, status="pending". See US-PAY-001 for complete payment lifecycle.
- **Space Status**: Computed field - "occupied" only if space has active agreement where current_date is between start/end dates
- **Future Enhancement (Phase 2)**:
  - Payment status will gate agreement activation (see US-PAY epic)
  - Custom end_date override: Admin can manually set end_date instead of auto-calculation for non-standard agreements

## UI Requirements
**Screen**: 合約管理 → "新增合約" modal
**Fields**:
- Customer (searchable dropdown)
- Space (available only)
- License Plates (required, "+ 新增車牌" button for additional plates)
- Type (radio: 日/月/季/年)
- Start Date (date picker)
- Price (auto-calculated, editable — see US-SPACE-003 for pricing model)

## Source
init_draft.md lines 26, 67, 104-107 | CLAUDE.md agreement lifecycle

## Dependencies
US-CUST-001, US-SPACE-001, US-SPACE-003 (pricing model), US-PAY-001 (payment lifecycle), US-AUDIT-002, US-LOC-003, US-LOC-004

## Test Data
Customer: 王小明 (0912-345-678) | Space: A區-01, tags=['有屋頂'], price=3600 | License Plates: ['ABC-1234', 'XYZ-9999'] | Type: 月租 | Start: 2026-02-01 → End: 2026-03-01 | Price: NT$3,600
