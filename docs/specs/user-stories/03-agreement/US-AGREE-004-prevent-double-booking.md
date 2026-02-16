# US-AGREE-004: Prevent Double-Booking (Date Range Overlap Validation)

**Priority**: Must Have | **Phase**: Phase 1 | **Sprint**: Sprint 3 (Weeks 5-6)
**Domain**: Agreement Management | **Epic**: Agreement Business Rules
**Status**: ✅ Implemented (commit a4443bc)

## User Story
As a parking lot admin, I want the system to prevent creating overlapping agreements for the same space, so that we avoid double-booking conflicts while allowing future reservations on currently occupied spaces.

## Acceptance Criteria
- **AC1**: Admin selects space + date range that overlaps existing agreement → Error: "車位 {name} 已被預訂" (DOUBLE_BOOKING error code)
- **AC2**: Date overlap validation uses range overlap formula (checks all non-terminated agreements):
  ```python
  # Two ranges overlap if:
  existing.start_date < new.end_date AND existing.end_date > new.start_date
  ```
- **AC3**: Non-overlapping agreements allowed:
  - Space A-01: Feb 1-28 (existing) + Mar 15-Apr 14 (new) → ✅ Allowed (no overlap)
  - Space A-01: Feb 1-28 (existing) + Feb 15-Mar 15 (new) → ❌ Blocked (overlap Feb 15-28)
  - Space A-01: Feb 1-Mar 1 (existing) + Mar 1-Apr 1 (new) → ✅ Allowed (back-to-back, end_date exclusive)
- **AC4**: Space dropdown shows all spaces with visual indicators:
  - "停車場 / A-01 ✓ 可用" (green) - No active agreement
  - "停車場 / A-01 (目前已占用)" (gray) - Has active agreement RIGHT NOW
  - Helper text: "可選擇未來日期預約車位（系統會檢查日期是否重疊）"
- **AC5**: Available spaces sorted first in dropdown
- **AC6**: Future agreements on occupied spaces allowed (if no date overlap)

## Business Rules
- **Date Range Validation**: Space can have multiple agreements if date ranges don't overlap
- **Overlap Formula**: Two ranges overlap if `range1.start < range2.end AND range1.end > range2.start`
- **Non-Terminated Check**: Validate against all non-terminated agreements (`terminated_at IS NULL`). Expired agreements may still block overlapping dates.
- **Terminated Agreements**: Excluded from overlap checks (their date range is released)
- **Back-to-Back Agreements**: Allowed when one ends exactly when next starts (e.g., Feb 1-Mar 1 + Mar 1-Apr 1) because end_date is exclusive
- **Future Agreements**: Allowed on currently occupied spaces if no date overlap (e.g., space occupied Feb-Mar can accept Apr-May agreement)
- **Multiple Future Agreements**: Allowed on same space with different non-overlapping periods
- **Space Status**: Computed field - only "occupied" if current_date is within an active agreement's date range

## UI Requirements
- Space dropdown: Shows **all spaces** (not filtered by status)
- Visual indicators:
  - ✓ 可用 (green) - Available spaces sorted first
  - (目前已占用) (gray) - Currently occupied spaces
- Helper text: "可選擇未來日期預約車位（系統會檢查日期是否重疊）"

## Implementation Notes

### Backend: Date Range Overlap Check (FastAPI Service Layer)

**File**: `backend/app/services/agreement_service.py`

```python
# Calculate end_date first (needed for overlap check)
end_date = _calc_end_date(data.start_date, data.agreement_type)

# Check for overlapping agreements on this space (date range validation)
overlap_result = await self.db.execute(
    select(Agreement).where(
        Agreement.space_id == data.space_id,
        Agreement.terminated_at.is_(None),
        Agreement.start_date < end_date,      # Existing starts before new ends
        Agreement.end_date > data.start_date, # Existing ends after new starts
    )
)
existing = overlap_result.scalar_one_or_none()
if existing:
    raise DoubleBookingError(space.name)
```

**Overlap Logic Explanation**:
- `existing.start_date < new.end_date` → Catches agreements that start before new one ends
- `existing.end_date > new.start_date` → Catches agreements that end after new one starts
- Both conditions true = overlap exists
- Either condition false = no overlap (e.g., one ends before other starts)

### Frontend: Space Selection UX

**File**: `frontend/src/app/(dashboard)/agreements/page.tsx`

```typescript
// Fetch all spaces (not filtered by status)
api.get<Space[]>("/api/v1/spaces")

// Sort and display with status indicators
spaces
  .sort((a, b) => {
    // Show available spaces first
    if (a.computed_status === "available" && b.computed_status !== "available") return -1;
    if (a.computed_status !== "available" && b.computed_status === "available") return 1;
    return (a.site_name || "").localeCompare(b.site_name || "");
  })
  .map((s) => (
    <SelectItem key={s.id} value={s.id}>
      <span className="flex items-center gap-2">
        <span>{s.site_name} / {s.name}</span>
        {s.computed_status === "occupied" && (
          <span className="text-xs text-muted-foreground">(目前已占用)</span>
        )}
        {s.computed_status === "available" && (
          <span className="text-xs text-green-600">✓ 可用</span>
        )}
      </span>
    </SelectItem>
  ))
```

## Test Coverage

**File**: `backend/tests/test_agreement_overlap.py` (5 comprehensive tests)

### ✅ Test Cases Passing

1. **`test_future_agreement_on_occupied_space`**
   - Scenario: Space occupied today → next month, create agreement 2 months from now
   - Expected: ✅ Allowed (no overlap)
   - Validates: Future agreements on currently occupied spaces

2. **`test_back_to_back_agreements`**
   - Scenario: First agreement Mar 1-Apr 1, second agreement Apr 1-May 1
   - Expected: ✅ Allowed (end_date exclusive)
   - Validates: Consecutive agreements with same boundary date

3. **`test_contained_agreement_rejected`**
   - Scenario: Large agreement Feb 1-Apr 1, attempt small agreement Mar 10-Mar 11
   - Expected: ❌ Blocked (contained within existing)
   - Validates: Fully contained agreements rejected

4. **`test_multiple_future_agreements_no_overlap`**
   - Scenario: Create agreements for Apr, Jun, Aug (gaps in May, Jul)
   - Expected: ✅ All allowed (no overlaps)
   - Validates: Multiple non-overlapping future agreements

5. **`test_terminated_agreement_allows_overlap`**
   - Scenario: Create agreement Mar 1-Apr 1, terminate it, create overlapping Mar 15-Apr 15
   - Expected: ✅ Allowed (terminated doesn't count)
   - Validates: Terminated agreements release their date range

**Updated Existing Test**: `backend/tests/test_agreements.py::test_double_booking_prevented`
- Changed from back-to-back (Mar 1-Apr 1 + Apr 1-May 1) to real overlap (Feb 15-Mar 15 + Feb 20-Mar 20)
- Expected: ❌ Blocked (actual overlap)

### Test Results
- **Total Tests**: 88 (84 → 88, added 4 new overlap tests)
- **All Passing**: ✅ 100% pass rate
- **Coverage**: Date range validation, back-to-back, containment, future agreements, termination

## Verification Method (Manual E2E)
1. Create agreement for A區-01 (Feb 1-Mar 1) ✓
2. Create agreement for A區-01 (Apr 1-May 1) → ✅ Success (no overlap)
3. Create agreement for A區-01 (Mar 1-Apr 1) → ✅ Success (back-to-back)
4. Attempt agreement for A區-01 (Feb 15-Mar 15) → ❌ Error "車位 A區-01 已被預訂" (overlaps Feb agreement)
5. Terminate Feb agreement → Create Mar 15-Apr 15 → ✅ Success (terminated doesn't block)
6. Frontend: Space dropdown shows all spaces with status indicators
7. Frontend: Helper text explains future agreements

## Source
- init_draft.md lines 76-77
- CLAUDE.md business rules
- bugs/future-agreements-overlap-validation.md (implementation plan)

## Dependencies
- US-AGREE-001 (Create Agreement)
- US-AGREE-006 (Computed Status)
- US-SPACE-001 (Space Management)
- US-SPACE-004 (Computed Space Status)

## Related Commits
- `a4443bc` - Fix: Implement date range overlap validation for future agreements (Feb 16, 2026)
