# US-AGREE-004: Prevent Double-Booking (One Space, One Active Agreement)

**Priority**: Must Have | **Phase**: Phase 1 | **Sprint**: Sprint 3 (Weeks 5-6)
**Domain**: Agreement Management | **Epic**: Agreement Business Rules

## User Story
As a parking lot admin, I want the system to prevent creating overlapping agreements for the same space, so that we avoid double-booking conflicts while allowing future reservations.

## Acceptance Criteria
- **AC1**: Admin selects space + date range that overlaps existing agreement → Error: "此車位在選定日期已被分配 (2026-02-01 至 2026-03-01)"
- **AC2**: Date overlap validation query (checks all non-terminated agreements):
  ```sql
  SELECT * FROM agreements
  WHERE space_id = :space_id
  AND status != 'terminated'
  AND (start_date, end_date) OVERLAPS (:new_start, :new_end)
  ```
  If returns rows → Block creation
- **AC3**: Non-overlapping agreements allowed:
  - Space A-01: Feb 1-28 (existing) + Mar 15-Apr 14 (new) → ✅ Allowed
  - Space A-01: Feb 1-28 (existing) + Feb 15-Mar 15 (new) → ❌ Blocked
- **AC4**: Space dropdown shows all spaces with visual indicators:
  - "A區-01 (可用)" - No agreements
  - "A區-01 (部分預訂)" - Has future agreements
  - "A區-01 (已佔用)" - Has active agreement RIGHT NOW
- **AC5**: Space detail shows timeline calendar with all existing agreements
- **AC6**: Race condition protection: Database trigger enforces validation atomically

## Business Rules
- **Date Range Validation**: Space can have multiple agreements if date ranges don't overlap
- **Non-Terminated Check**: Validate against all non-terminated agreements (status != 'terminated'). Expired agreements naturally don't overlap with future dates.
- **Terminated Agreements**: Only terminated agreements are excluded from overlap checks (their date range is released)
- **Atomicity**: Validation + creation in single transaction
- **Space Status**: Computed field - only "occupied" if current_date is within an active agreement's date range

## UI Requirements
Space dropdown filters: `status='available' AND no active agreement` | Display: "Site - Space (可用)"

## Implementation Notes

**Database Trigger Function** (enforces date overlap validation atomically):
```sql
CREATE OR REPLACE FUNCTION check_space_date_overlap()
RETURNS TRIGGER AS $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM agreements
    WHERE space_id = NEW.space_id
    AND id != COALESCE(NEW.id, -1)  -- Exclude current record on UPDATE
    AND status != 'terminated'  -- Only terminated agreements release their date range
    AND (NEW.start_date, NEW.end_date) OVERLAPS (start_date, end_date)
  ) THEN
    RAISE EXCEPTION '此車位在選定日期已被分配';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER validate_space_availability
BEFORE INSERT OR UPDATE ON agreements
FOR EACH ROW EXECUTE FUNCTION check_space_date_overlap();
```

## Verification Method
1. Create agreement for A區-01 (Feb 1-28) ✓
2. Create agreement for A區-01 (Mar 15-Apr 14) → ✅ Success (no overlap)
3. Attempt agreement for A區-01 (Feb 15-Mar 15) → ❌ Error (overlaps Feb period)
4. First agreement expires (status="expired") → Still blocks overlap (status check includes pending/active only)

## Source
init_draft.md lines 76-77 | CLAUDE.md business rules

## Dependencies
US-AGREE-001, US-AGREE-006, US-SPACE-001

## Test Data
Space A區-01 | Agreement 1: active → blocks | Agreement 1 expired → allows Agreement 2
