# US-LOC-004: Taiwan Date Format (YYYY年MM月DD日 / ISO for Forms)

**Priority**: Must Have
**Phase**: Phase 1
**Domain**: Localization
**Epic**: Taiwan Localization
**Sprint**: Sprint 2 (Weeks 3-4)

## User Story

As a parking lot admin,
I want dates displayed in familiar Taiwan format (YYYY年MM月DD日) and forms to use ISO format (YYYY-MM-DD),
So that dates are easy to read and input.

## Acceptance Criteria

- **AC1**: All read-only date displays use Taiwan format: `YYYY年MM月DD日`
  - Example: `2026年02月15日` (February 15, 2026)
- **AC2**: Date input fields use ISO format for input clarity: `YYYY-MM-DD`
  - Example: `2026-02-15`
- **AC3**: Date range labels in Traditional Chinese:
  - 今天 (Today), 昨天 (Yesterday), 本週 (This Week), 本月 (This Month)
- **AC4**: Time displays use 24-hour format: `HH:mm` (e.g., 14:30)
- **AC5**: Relative date displays in Traditional Chinese:
  - "剛剛" (Just now), "X 分鐘前" (X minutes ago), "X 小時前" (X hours ago), "X 天前" (X days ago)
- **AC6**: Date validation messages in Traditional Chinese:
  - Empty: "日期為必填欄位"
  - Invalid: "請輸入有效的日期"
  - Past date: "日期不可為過去時間"
  - End before start: "結束日期不可早於開始日期"
- **AC7**: CSV import/export uses ISO format (YYYY-MM-DD)

## Business Rules

- Display Format: Taiwan format (YYYY年MM月DD日) for human readability
- Input Format: ISO format (YYYY-MM-DD) for forms
- Storage: ISO format in database
- Time Zone: Taiwan Standard Time (UTC+8)
- Week Start: Monday

## UI Requirements

- **Affected Screens**: 合約管理 (agreement dates), 付款管理 (payment dates), 儀表板, 報表, 系統設定 → 系統日誌, CSV
- **Display Format**: `YYYY年MM月DD日` (e.g., `2026年02月15日`)
- **Input Format**: Native `<input type="date">` with ISO format
- **Date Pickers**: Support Traditional Chinese locale

## Source

- init_draft.md line 158

## Dependencies

- US-AGREE-001 (agreement with dates)
- US-PAY-001 (payment with date)
- US-AUDIT-001 (audit log timestamps)

## Related Stories

- US-LOC-001 (Traditional Chinese labels)
- US-AGREE-002 (auto-calculate end dates)

## Test Data

- Agreement start: 2026-02-15 → Display: `2026年02月15日`
- Agreement end: 2026-03-15 → Display: `2026年03月15日`
- Payment date: 2026-02-20 → Display: `2026年02月20日`
- Recent activity: 10 minutes ago → Display: `10 分鐘前`
