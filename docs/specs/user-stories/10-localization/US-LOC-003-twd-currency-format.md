# US-LOC-003: TWD Currency Format (NT$1,234)

**Priority**: Must Have
**Phase**: Phase 1
**Domain**: Localization
**Epic**: Taiwan Localization
**Sprint**: Sprint 2 (Weeks 3-4)

## User Story

As a parking lot admin,
I want all prices and payment amounts displayed in TWD format (NT$ with comma separators),
So that financial information is clear and follows Taiwan conventions.

## Acceptance Criteria

- **AC1**: All price and payment amount fields display with NT$ prefix and comma thousands separators
  - Example: `NT$3,600` for 3600 TWD
- **AC2**: Given a price of 1000 or greater, format includes comma separator:
  - 1000 → `NT$1,000`, 3600 → `NT$3,600`, 12000 → `NT$12,000`
- **AC3**: Given a price less than 1000, format includes NT$ prefix without comma:
  - 500 → `NT$500`, 100 → `NT$100`
- **AC4**: Price input fields accept plain numbers and auto-format to NT$ on blur
- **AC5**: Invalid price input shows error in Traditional Chinese:
  - Negative: "價格不可為負數"
  - Non-numeric: "請輸入有效的數字"
  - Decimal: "價格必須為整數"
- **AC6**: Price calculations display final result in NT$ format with commas
- **AC7**: Reports, CSV exports, and print views all use NT$ comma format

## Business Rules

- Currency: Taiwan Dollar (TWD, NT$) only for Phase 1
- Decimal Places: None (parking fees are whole numbers)
- Negative Values: Not allowed (prices must be ≥ 0)
- Display Format: Always include NT$ prefix and comma thousands separators
- Storage: Store as integer in database (without currency symbol or commas)

## UI Requirements

- **Affected Screens**: 停車場管理 (space price), 合約管理 (agreement price), 付款管理 (payment amount), 報表, CSV Import/Export
- **Input Format**: Allow plain numbers, auto-format to NT$ on blur
- **Display Format**: Always NT$ with commas (read-only fields and tables)

## Source

- init_draft.md line 157

## Dependencies

- US-SPACE-001 (space with price)
- US-AGREE-001 (agreement with price)
- US-PAY-001 (payment with amount)

## Related Stories

- US-LOC-001 (Traditional Chinese error messages)
- US-RPT-003 (revenue report)

## Test Data

- Space price: 3000 → Display: `NT$3,000`
- Agreement price: 12000 → Display: `NT$12,000`
- Payment amount: 3600 → Display: `NT$3,600`
- Invalid: "-500" → Error: "價格不可為負數"
