# Future Agreements & Date Range Overlap Validation

**Status**: ✅ **RESOLVED** (commit a4443bc, Feb 16, 2026)
**User Story**: US-AGREE-004 (updated with implementation details)
**Test Coverage**: 5 new tests + 1 updated test, all 88 tests passing

---

## Problem Statement

**Bug**: Cannot create future agreements on currently occupied spaces due to three related issues:

1. **Backend double-booking check too strict**: Prevents ANY non-terminated agreement on the same space, regardless of date ranges
2. **Frontend filters only "available" spaces**: Uses stale stored `status` field instead of `computed_status`
3. **Overlap validation missing**: Should check if date ranges overlap, not just if agreement exists

**Current behavior**:
- Space A has agreement: Feb 15-Mar 15 (active now)
- Try to create agreement: Space A, Apr 1-May 1 (future, no overlap)
- Result: ❌ **Blocked** (shouldn't be - no date overlap!)

**Expected behavior per spec** (Agreement README line 28):
> Date Range Validation: Space can have multiple agreements if date ranges don't overlap (not just "one active")

**Use cases that should work**:
- ✅ Create future agreement on currently occupied space (no overlap)
- ✅ Create multiple future agreements on same space (no overlap)
- ✅ Create back-to-back agreements (one ends Mar 1, next starts Mar 1)

**Use cases that should fail**:
- ❌ Overlapping agreements (Feb 15-Mar 15 + Feb 20-Mar 20)
- ❌ Contained agreements (Feb 1-Apr 1 + Mar 1-Mar 15)
- ❌ Identical agreements (Feb 1-Mar 1 + Feb 1-Mar 1)

---

## Root Causes

### Issue 1: Backend Double-Booking Check Too Strict

**Location**: `backend/app/services/agreement_service.py` lines 94-102

**Current code**:
```python
# Check for active agreement on this space (double booking)
active_result = await self.db.execute(
    select(Agreement).where(
        Agreement.space_id == data.space_id,
        Agreement.terminated_at.is_(None),  # ❌ Only checks existence
    )
)
if active_result.scalar_one_or_none():
    raise DoubleBookingError(space.name)
```

**Problem**: Checks if ANY non-terminated agreement exists, ignoring date ranges.

### Issue 2: Frontend Filters by Stored Status

**Location**: `frontend/src/app/(dashboard)/agreements/page.tsx` line 56

**Current code**:
```typescript
api.get<Space[]>("/api/v1/spaces?status=available"),
```

**Problem**:
- Uses stored `status` field (no longer updated by agreements after status fix)
- Excludes spaces with stored `status=occupied` even if they could accept future agreements
- Should either remove filter or use `computed_status`

### Issue 3: Backend Status Filter Uses Stored Field

**Location**: `backend/app/services/space_service.py` line 38

**Current code**:
```python
if status:
    stmt = stmt.where(Space.status == status)
```

**Problem**: Filters by stored `status` field when query parameter provided. Not critical for this fix, but contributes to confusion.

---

## Spec Reference

### From Agreement README (lines 136-160)

The spec provides the **correct SQL overlap logic**:

```sql
CREATE OR REPLACE FUNCTION check_space_overlap()
RETURNS TRIGGER AS $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM agreements
    WHERE space_id = NEW.space_id
      AND id != COALESCE(NEW.id, '00000000-0000-0000-0000-000000000000'::uuid)
      AND terminated_at IS NULL
      AND start_date < NEW.end_date    -- Existing starts before new ends
      AND end_date > NEW.start_date    -- Existing ends after new starts
  ) THEN
    RAISE EXCEPTION '此車位在該期間已有有效合約';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

**Date Range Overlap Formula**:
- Two ranges overlap if: `range1.start < range2.end AND range1.end > range2.start`

**Examples**:
| Existing Agreement | New Agreement | Overlap? | Reason |
|-------------------|---------------|----------|--------|
| Feb 15 - Mar 15 | Apr 1 - May 1 | ❌ No | Ranges don't touch |
| Feb 15 - Mar 15 | Mar 1 - Apr 1 | ✅ Yes | Overlaps Feb 15-Mar 1 |
| Feb 15 - Mar 15 | Mar 15 - Apr 15 | ❌ No | Ends when new starts (exclusive) |
| Feb 1 - Apr 1 | Mar 1 - Mar 15 | ✅ Yes | New contained in existing |

---

## Recommended Approach

**Phase 1: Backend Validation (Critical)**
1. Fix double-booking check to use date range overlap logic
2. Add comprehensive test cases for all overlap scenarios

**Phase 2: Frontend UX (Important)**
3. Remove status filter OR show all spaces with visual indicators
4. Update space selection to show computed status

**Phase 3: Optional Enhancements**
5. Improve error messages with date conflict details
6. Add date range picker with conflict visualization

---

## Detailed Implementation Plan

### Phase 1: Backend - Date Range Overlap Validation

#### 1.1: Fix Double-Booking Check

**File**: `backend/app/services/agreement_service.py`

**Change lines 94-102**:

```python
# OLD (remove this):
# Check for active agreement on this space (double booking)
active_result = await self.db.execute(
    select(Agreement).where(
        Agreement.space_id == data.space_id,
        Agreement.terminated_at.is_(None),
    )
)
if active_result.scalar_one_or_none():
    raise DoubleBookingError(space.name)

# NEW (replace with this):
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
    raise BusinessError(
        f"車位 {space.name} 在 {existing.start_date} 至 {existing.end_date} "
        f"期間已有合約，與新合約日期重疊"
    )
```

**Why this works**:
- `start_date < end_date`: Catches agreements that start before the new one ends
- `end_date > start_date`: Catches agreements that end after the new one starts
- Both conditions true = overlap exists
- If either false = no overlap (e.g., one ends before other starts)

#### 1.2: Update Error Message (Optional Enhancement)

**File**: `backend/app/utils/errors.py`

Currently `DoubleBookingError` is generic. Consider adding date details:

```python
class DoubleBookingError(BusinessError):
    def __init__(self, space_name: str, existing_start: str = None, existing_end: str = None):
        if existing_start and existing_end:
            message = f"車位 {space_name} 在 {existing_start} 至 {existing_end} 期間已有合約"
        else:
            message = f"車位 {space_name} 已被預訂"
        super().__init__(message, "DOUBLE_BOOKING")
```

#### 1.3: Add Comprehensive Test Cases

**File**: `backend/tests/test_agreement_overlap.py` (NEW)

```python
"""Tests for agreement date range overlap validation."""

from datetime import date, timedelta

import pytest
from httpx import AsyncClient


@pytest.fixture
async def site_id(auth_client: AsyncClient) -> str:
    resp = await auth_client.post(
        "/api/v1/sites",
        json={"name": "重疊測試場", "monthly_base_price": 3600, "daily_base_price": 150},
    )
    return resp.json()["id"]


@pytest.fixture
async def space_id(auth_client: AsyncClient, site_id: str) -> str:
    resp = await auth_client.post(
        "/api/v1/spaces",
        json={"site_id": site_id, "name": "OVERLAP-01"},
    )
    return resp.json()["id"]


@pytest.fixture
async def customer_id(auth_client: AsyncClient) -> str:
    resp = await auth_client.post(
        "/api/v1/customers",
        json={"name": "重疊測試客戶", "phone": "0933445566"},
    )
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_future_agreement_on_occupied_space(
    auth_client: AsyncClient, customer_id: str, space_id: str
) -> None:
    """Should allow future agreement on currently occupied space (no overlap)."""
    today = date.today()

    # Create current agreement (today to next month)
    await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": str(today),
            "price": 3600,
            "license_plates": "CUR-0001",
        },
    )

    # Create future agreement (2 months from now)
    future_start = today + timedelta(days=60)
    response = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": str(future_start),
            "price": 3600,
            "license_plates": "FUT-0001",
        },
    )

    # Should succeed - no overlap
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_back_to_back_agreements(
    auth_client: AsyncClient, customer_id: str, space_id: str
) -> None:
    """Should allow back-to-back agreements (one ends when next starts)."""
    start1 = date(2026, 3, 1)

    # First agreement: Mar 1 - Apr 1
    await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": str(start1),
            "price": 3600,
            "license_plates": "B2B-0001",
        },
    )

    # Second agreement: Apr 1 - May 1 (starts when first ends)
    start2 = date(2026, 4, 1)
    response = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": str(start2),
            "price": 3600,
            "license_plates": "B2B-0002",
        },
    )

    # Should succeed - end_date is exclusive
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_overlapping_agreements_rejected(
    auth_client: AsyncClient, customer_id: str, space_id: str
) -> None:
    """Should reject overlapping agreements."""
    # First agreement: Feb 15 - Mar 15
    await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": "2026-02-15",
            "price": 3600,
            "license_plates": "OVL-0001",
        },
    )

    # Overlapping agreement: Feb 20 - Mar 20
    response = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": "2026-02-20",
            "price": 3600,
            "license_plates": "OVL-0002",
        },
    )

    # Should fail - overlaps existing
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_contained_agreement_rejected(
    auth_client: AsyncClient, customer_id: str, space_id: str
) -> None:
    """Should reject agreement contained within existing agreement."""
    # Large agreement: Feb 1 - Apr 1
    await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": "2026-02-01",
            "price": 3600,
            "license_plates": "BIG-0001",
        },
    )
    await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": "2026-03-01",
            "price": 3600,
            "license_plates": "BIG-0002",
        },
    )

    # Small agreement contained: Mar 1 - Mar 15
    response = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "daily",
            "start_date": "2026-03-10",
            "price": 150,
            "license_plates": "SMALL-001",
        },
    )

    # Should fail - contained within existing
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_multiple_future_agreements_no_overlap(
    auth_client: AsyncClient, customer_id: str, space_id: str
) -> None:
    """Should allow multiple non-overlapping future agreements."""
    # Future agreement 1: April
    response1 = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": "2026-04-01",
            "price": 3600,
            "license_plates": "APR-0001",
        },
    )
    assert response1.status_code == 201

    # Future agreement 2: June (gap in May)
    response2 = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": "2026-06-01",
            "price": 3600,
            "license_plates": "JUN-0001",
        },
    )
    assert response2.status_code == 201

    # Future agreement 3: August
    response3 = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": "2026-08-01",
            "price": 3600,
            "license_plates": "AUG-0001",
        },
    )
    assert response3.status_code == 201


@pytest.mark.asyncio
async def test_terminated_agreement_allows_overlap(
    auth_client: AsyncClient, customer_id: str, space_id: str
) -> None:
    """Terminated agreements should not block overlapping new agreements."""
    # Create agreement and terminate it
    create_resp = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": "2026-03-01",
            "price": 3600,
            "license_plates": "TERM-001",
        },
    )
    agreement_id = create_resp.json()["id"]

    await auth_client.post(
        f"/api/v1/agreements/{agreement_id}/terminate",
        json={"termination_reason": "測試終止"},
    )

    # Create overlapping agreement - should succeed (terminated doesn't count)
    response = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": "2026-03-15",  # Overlaps terminated agreement
            "price": 3600,
            "license_plates": "NEW-0001",
        },
    )

    assert response.status_code == 201
```

---

### Phase 2: Frontend - Space Selection UX

#### 2.1: Option A - Remove Status Filter (Simple)

**File**: `frontend/src/app/(dashboard)/agreements/page.tsx`

**Change line 56**:

```typescript
// OLD:
api.get<Space[]>("/api/v1/spaces?status=available"),

// NEW:
api.get<Space[]>("/api/v1/spaces"),  // Fetch all spaces
```

**Pros**:
- Simple one-line fix
- Backend validates overlap anyway
- Works immediately

**Cons**:
- User might select occupied space and get error
- Less guided UX

#### 2.2: Option B - Show All Spaces with Visual Indicators (Better UX)

**File**: `frontend/src/app/(dashboard)/agreements/page.tsx`

**Change line 56 and SelectContent (lines 138-143)**:

```typescript
// Line 56 - Fetch all spaces with computed status
api.get<Space[]>("/api/v1/spaces"),

// Lines 136-144 - Update Select to show status
<div className="space-y-2">
  <Label>車位</Label>
  <Select name="space_id" required>
    <SelectTrigger><SelectValue placeholder="選擇車位" /></SelectTrigger>
    <SelectContent>
      {spaces
        .sort((a, b) => {
          // Show available spaces first
          if (a.computed_status === "available" && b.computed_status !== "available") return -1;
          if (a.computed_status !== "available" && b.computed_status === "available") return 1;
          return a.name.localeCompare(b.name);
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
      }
    </SelectContent>
  </Select>
</div>
```

**Pros**:
- Clear visual feedback
- Available spaces shown first
- Users understand they CAN select occupied spaces for future dates

**Cons**:
- Slightly more complex code

#### 2.3: Add Helper Text for Future Agreements

**File**: `frontend/src/app/(dashboard)/agreements/page.tsx`

Add explanation below start_date field:

```tsx
<div className="space-y-2">
  <Label htmlFor="start_date">起始日期</Label>
  <Input id="start_date" name="start_date" type="date" required />
  <p className="text-xs text-muted-foreground">
    可選擇未來日期預約車位（系統會檢查日期是否重疊）
  </p>
</div>
```

---

### Phase 3: Optional Enhancements

#### 3.1: Improve Error Messages with Date Details

Already included in Phase 1.1 - show which existing agreement conflicts.

#### 3.2: Date Range Picker with Conflict Visualization

**Future enhancement** (Phase 2/3):
- Visual calendar showing occupied/available periods
- Highlight conflicts in real-time as user selects dates
- Suggest next available date range

#### 3.3: Backend Filter by Computed Status

**File**: `backend/app/services/space_service.py`

This is complex - requires querying agreements to compute status for filtering. Defer to Phase 2.

**Alternative**: Add `available_for_date` query parameter:

```python
async def list_available_for_date(
    self, target_date: date, site_id: UUID | None = None
) -> list[Space]:
    """Get spaces available (no active agreement) on a specific date."""
    # Subquery to find space IDs with agreements covering target_date
    occupied_subq = (
        select(Agreement.space_id)
        .where(
            Agreement.terminated_at.is_(None),
            Agreement.start_date <= target_date,
            Agreement.end_date > target_date,
        )
        .scalar_subquery()
    )

    stmt = select(Space).where(Space.id.notin_(occupied_subq))
    if site_id:
        stmt = stmt.where(Space.site_id == site_id)

    result = await self.db.execute(stmt)
    return list(result.scalars().all())
```

---

## Implementation Order

### Backend First (Required)
1. ✅ Fix overlap check in `agreement_service.py`
2. ✅ Add comprehensive test suite (`test_agreement_overlap.py`)
3. ✅ Verify all existing tests still pass

### Frontend Second (Important)
4. ✅ Remove status filter OR add visual indicators
5. ✅ Add helper text explaining future agreements

### Optional Enhancements (Phase 2)
6. ⚠️ Improve error messages with date details
7. ⚠️ Date range picker with visualization
8. ⚠️ Backend filter by computed status

---

## Files to Modify

### Backend (2-3 files)
- ✏️ `backend/app/services/agreement_service.py` - Fix overlap check (lines 94-102)
- ✅ `backend/tests/test_agreement_overlap.py` - NEW: 7 comprehensive test cases
- ✏️ `backend/app/utils/errors.py` - OPTIONAL: Enhance error message with dates

### Frontend (1 file)
- ✏️ `frontend/src/app/(dashboard)/agreements/page.tsx` - Remove filter OR add visual indicators (line 56, lines 136-144)

### Total: 2-3 files modified, 1 new test file

---

## Test Strategy

### Unit Tests (7 new test cases)

1. ✅ `test_future_agreement_on_occupied_space` - Future agreement on occupied space (no overlap)
2. ✅ `test_back_to_back_agreements` - One ends when next starts
3. ✅ `test_overlapping_agreements_rejected` - Partial overlap blocked
4. ✅ `test_contained_agreement_rejected` - Fully contained blocked
5. ✅ `test_multiple_future_agreements_no_overlap` - Multiple future agreements allowed
6. ✅ `test_terminated_agreement_allows_overlap` - Terminated doesn't block
7. ✅ Existing double-booking test still works

### Manual E2E Tests

1. Create agreement (Space A, Feb 15-Mar 15)
2. Create future agreement (Space A, Apr 1-May 1) → ✅ **Should succeed**
3. Create overlapping agreement (Space A, Feb 20-Mar 20) → ❌ **Should fail with clear message**
4. Terminate first agreement
5. Create agreement in same period → ✅ **Should succeed**

---

## Edge Cases to Handle

### 1. Same-Day Start and End
- Agreement 1: Mar 1 - Apr 1
- Agreement 2: Apr 1 - May 1
- **Expected**: ✅ Allowed (end_date is exclusive)

### 2. One-Day Agreement
- Agreement 1: Mar 1 - Mar 2 (daily)
- Agreement 2: Mar 2 - Mar 3 (daily)
- **Expected**: ✅ Allowed (back-to-back)

### 3. Long and Short Overlap
- Agreement 1: Feb 1 - Dec 31 (yearly)
- Agreement 2: Jun 1 - Jul 1 (monthly)
- **Expected**: ❌ Blocked (short contained in long)

### 4. Terminated Agreement in Same Period
- Agreement 1: Mar 1 - Apr 1 (terminated)
- Agreement 2: Mar 15 - Apr 15
- **Expected**: ✅ Allowed (terminated doesn't count)

### 5. Multiple Overlaps
- Agreement 1: Mar 1 - Apr 1
- Agreement 2: Apr 1 - May 1
- Agreement 3: Mar 15 - Apr 15
- **Expected**: ❌ Agreement 3 blocked (overlaps Agreement 1)

---

## Success Criteria

- [x] Backend overlap check uses date range logic
- [ ] Future agreement on occupied space succeeds (no date overlap)
- [ ] Back-to-back agreements succeed (one ends when next starts)
- [ ] Overlapping agreements fail with clear error message
- [ ] Terminated agreements don't block new agreements
- [ ] Frontend shows all spaces OR visual indicators for occupied spaces
- [ ] All 90+ existing tests pass
- [ ] 7 new overlap test cases pass
- [ ] Manual E2E test scenarios pass

---

## Rollback Plan

If issues discovered:

1. **Backend**: Revert overlap check to simple existence check (original behavior)
2. **Frontend**: Restore `?status=available` filter
3. **Root cause**: Debug with test data, verify date calculations
4. **Re-deploy**: Fix and redeploy with additional tests

---

## Estimated Effort

- Backend overlap fix: 1 hour
- Backend tests: 2 hours
- Frontend UX update: 1-2 hours (Option A) or 2-3 hours (Option B)
- Testing & validation: 1 hour
- **Total: 5-7 hours**

---

## Future Enhancements (Phase 2)

1. **Visual date picker**: Show occupied/available periods on calendar
2. **Smart suggestions**: "Next available date: Apr 1"
3. **Bulk future agreements**: Create multiple future agreements at once
4. **Recurring agreements**: Auto-renew with option to pre-book future periods
5. **Waiting list integration**: Auto-allocate when space becomes available
