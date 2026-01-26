# US-LOC-002: Taiwan Phone Number Format (09XX-XXX-XXX)

**Priority**: Must Have
**Phase**: Phase 1
**Domain**: Localization
**Epic**: Taiwan Localization
**Sprint**: Sprint 2 (Weeks 3-4)

## User Story

As a parking lot admin,
I want all phone numbers displayed and validated in Taiwan mobile format (09XX-XXX-XXX),
So that contact information is consistent and easy to read.

## Acceptance Criteria

- **AC1**: All phone number display fields format as 09XX-XXX-XXX (e.g., 0912-345-678)
- **AC2**: Phone input fields accept multiple formats and auto-format on blur:
  - Input: `0912345678` → Display: `0912-345-678`
  - Input: `0912-345-678` → Display: `0912-345-678`
  - Input: `0912 345 678` → Display: `0912-345-678`
- **AC3**: System validates phone numbers match Taiwan mobile pattern:
  - Starts with 09, exactly 10 digits total
- **AC4**: Invalid phone input shows error in Traditional Chinese:
  - Empty: "手機號碼為必填欄位"
  - Invalid format: "請輸入有效的台灣手機號碼 (格式: 09XX-XXX-XXX)"
  - Wrong prefix: "台灣手機號碼必須以 09 開頭"
  - Wrong length: "手機號碼必須為 10 位數字"
- **AC5**: Phone numbers in CSV import/export use 09XX-XXX-XXX format
- **AC6**: Phone numbers in reports and print views use 09XX-XXX-XXX format

## Business Rules

- Taiwan Mobile Format: 09XX-XXX-XXX (10 digits starting with 09)
- Storage: Normalized without dashes in database (0912345678)
- Display: Always formatted with dashes (0912-345-678)
- Validation: Taiwan mobile numbers only (landlines not supported in Phase 1)

## UI Requirements

- **Affected Screens**: 客戶管理, 合約管理, 候補名單, 報表, CSV Import/Export
- **Input Mask**: Use input mask library for auto-formatting
- **Placeholder**: "09XX-XXX-XXX"

## Source

- init_draft.md line 156

## Dependencies

- US-CUST-001 (customer creation)
- US-BULK-001 (CSV import)

## Related Stories

- US-LOC-001 (Traditional Chinese error messages)

## Test Data

- Valid: 0912-345-678, 0912345678, 0912 345 678 → All display as 0912-345-678
- Invalid: 0812-345-678 → Error (wrong prefix)
- Invalid: 912-345-678 → Error (too short)
