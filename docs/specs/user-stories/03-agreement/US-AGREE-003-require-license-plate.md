# US-AGREE-003: Require At Least One License Plate, Allow Multiple

**Priority**: Must Have | **Phase**: Phase 1 | **Sprint**: Sprint 3 (Weeks 5-6)
**Domain**: Agreement Management | **Epic**: Agreement Data Validation

## User Story
As a parking lot admin, I want agreements to require at least one license plate but allow multiple plates, so that customers with multiple vehicles or who switch vehicles can use the same parking space.

## Acceptance Criteria
- **AC1**: Agreement without at least one license plate → Error: "至少需要一個車牌號碼"
- **AC2**: First license plate field marked required with red asterisk (*)
- **AC3**: Each plate validates Taiwan format: ABC-1234, XYZ-9999 (3-8 chars, alphanumeric + hyphens)
- **AC4**: Invalid format → Error: "車牌號碼格式不正確 (3-8個字元)"
- **AC5**: Agreement detail displays all license plates in uppercase badges: "ABC-1234" "XYZ-9999"
- **AC6**: Database enforces at least one plate: `CHECK (array_length(license_plates, 1) >= 1)`
- **AC7**: **Future Requirement (Should Have - CSV Import)**: CSV import validates at least one license_plate provided (comma-separated format if multiple: "ABC-1234,XYZ-9999")
- **AC8**: Admin can add multiple license plates: Click "+ 新增車牌" → Enter additional plate → Save → All plates stored in `license_plates` array
- **AC9**: Admin can remove license plates (minimum 1 must remain) → Error if trying to delete last plate: "至少需要保留一個車牌號碼"

## Business Rules
- **Minimum**: 1 license plate required for ALL agreement types (daily/monthly/quarterly/yearly)
- **Maximum**: No hard limit (practical max ~5 plates per agreement)
- **Use Case**: Customer has multiple vehicles using same space, or switches vehicles during rental period
- **Format**: Taiwan vehicle plate (alphanumeric, 3-8 characters)
- **Normalization**: Store uppercase for consistent search
- **NOT Unique**: Same plate can appear in multiple agreements over time (historical tracking)
- **Database Storage**: PostgreSQL TEXT[] array (e.g., `['ABC-1234', 'XYZ-9999']`)
- **Privacy**: All plates visible to admins only (masked for public per US-SEC-006)

## UI Requirements
**Initial Plate**: Label: 車牌號碼 * | Placeholder: "ABC-1234" | Auto-uppercase | Max: 8 chars | Pattern: [A-Z0-9-]{3,8}
**Additional Plates**: Button: "+ 新增車牌" (below first plate) → Click opens new input field → Enter plate → Auto-adds to list
**Display**: Show all plates as removable badges with "×" button (disabled on last plate)

## Source
init_draft.md lines 8, 26, 27, 67 | CLAUDE.md business rules

## Dependencies
US-AGREE-001, US-SEC-006

## Test Data
**Single Plate**: Valid: "ABC-1234", "abc-1234" (→ "ABC-1234") | Invalid: "AB" (too short), "ABCDEFGHI" (too long), "" (empty - error)
**Multiple Plates**: Valid: ["ABC-1234", "XYZ-9999", "DEF-5678"] | Database: `{ABC-1234,XYZ-9999,DEF-5678}` (PostgreSQL array format)
**CSV Import**: Single: "ABC-1234" | Multiple: "ABC-1234,XYZ-9999" (comma-separated)
