# Space Status Computed from Agreements + Agreement Links

## Problem Statement

**Bug**: Agreement creation immediately sets `space.status = "occupied"` regardless of start_date, violating the spec that says status should be computed based on whether `current_date` falls within an active agreement's date range.

**Current behavior**:
- Create agreement with `start_date = 2026-03-01` (future) → space becomes "occupied" immediately
- This is wrong: space should remain "available" until 2026-03-01

**Missing feature**: No link from space list/detail to view the current active agreement on that space.

## Specification (from US-AGREE-006)

Space status should be **computed on-the-fly**:
- **`occupied`** = Non-terminated agreement where `start_date ≤ current_date ≤ end_date`
- **`available`** = No active agreement covers current_date AND no manual status

Manual statuses (`maintenance`, `reserved`) override computed status (Phase 2 feature).

---

## Recommended Approach: Computed Status

### Core Principle
**Remove all space.status mutations from agreement lifecycle code.** Status becomes a read-only computed property based on agreement data.

### Why This Approach?

1. **Single Source of Truth**: Agreement dates are the authoritative source for occupancy
2. **Always Accurate**: No risk of stale status (e.g., expired agreement still showing space as occupied)
3. **No Background Jobs**: Status updates automatically when `current_date` changes
4. **Simpler Logic**: Agreement service doesn't need to manage space state
5. **Spec Compliance**: Matches US-AGREE-006 exactly

---

## Detailed Implementation Plan

### Phase 1: Backend - Computed Status

#### 1.1: Add Helper to Compute Space Status

**File**: `backend/app/services/space_service.py`

Add method:
```python
async def compute_status(self, space: Space) -> str:
    """Compute space status based on active agreements.

    Returns:
        "occupied" if current_date is within any non-terminated agreement
        "available" otherwise
    """
    from datetime import date
    from app.models.agreement import Agreement

    today = date.today()

    result = await self.db.execute(
        select(Agreement).where(
            Agreement.space_id == space.id,
            Agreement.terminated_at.is_(None),
            Agreement.start_date <= today,
            Agreement.end_date >= today,
        ).limit(1)
    )

    if result.scalar_one_or_none():
        return "occupied"
    return "available"
```

**Alternative**: Add as a method on the `Space` model itself (requires session injection).

#### 1.2: Update SpaceResponse to Include Computed Status

**File**: `backend/app/schemas/space.py`

```python
class SpaceResponse(BaseModel):
    # ... existing fields ...
    computed_status: str | None = None  # "available" or "occupied"
    active_agreement_id: UUID | None = None  # Link to current agreement
```

#### 1.3: Update Space API to Compute Status

**File**: `backend/app/api/spaces.py`

Update `_to_response()`:
```python
def _to_response(s: Space, all_tags: list[Tag] | None = None, svc: SpaceService | None = None) -> SpaceResponse:
    resp = SpaceResponse(
        # ... existing fields ...
        computed_status=None,  # Set below if svc provided
        active_agreement_id=None,
    )

    if svc:
        # Compute status
        resp.computed_status = await svc.compute_status(s)

        # Get active agreement if any
        active = await svc.get_active_agreement(s.id)
        if active:
            resp.active_agreement_id = active.id

        # Existing pricing logic
        if all_tags is not None:
            pricing = svc.compute_pricing(s, all_tags)
            # ...

    return resp
```

**Issue**: `_to_response()` is not async. Need to refactor or compute status in the route handlers.

**Better approach**: Compute status in route handlers, pass to `_to_response()`:

```python
@router.get("", response_model=list[SpaceResponse])
async def list_spaces(...):
    svc = SpaceService(db, current_user)
    spaces = await svc.list(...)
    all_tags = await svc.get_all_tags()

    # Compute status and active agreements for all spaces
    results = []
    for s in spaces:
        status = await svc.compute_status(s)
        active_agreement = await svc.get_active_agreement(s.id)
        pricing = svc.compute_pricing(s, all_tags)

        resp = SpaceResponse(
            # ... all fields ...
            computed_status=status,
            active_agreement_id=active_agreement.id if active_agreement else None,
            # pricing fields
        )
        results.append(resp)

    return results
```

#### 1.4: Add Helper to Get Active Agreement

**File**: `backend/app/services/space_service.py`

```python
async def get_active_agreement(self, space_id: UUID) -> Agreement | None:
    """Get the currently active agreement for this space, if any."""
    from datetime import date
    from app.models.agreement import Agreement

    today = date.today()

    result = await self.db.execute(
        select(Agreement).where(
            Agreement.space_id == space_id,
            Agreement.terminated_at.is_(None),
            Agreement.start_date <= today,
            Agreement.end_date >= today,
        ).limit(1)
    )

    return result.scalar_one_or_none()
```

#### 1.5: Remove Status Mutations from Agreement Service

**File**: `backend/app/services/agreement_service.py`

**Remove lines 130-131** (create):
```python
# REMOVE THIS
# Update space status to occupied
space.status = "occupied"
```

**Remove lines 169-175** (terminate):
```python
# REMOVE THIS
# Release space
space_result = await self.db.execute(
    select(Space).where(Space.id == agreement.space_id)
)
space = space_result.scalar_one_or_none()
if space:
    space.status = "available"
```

#### 1.6: Update Space Status Field Documentation

**File**: `backend/app/models/space.py`

Update comment on line 17-19:
```python
status: Mapped[str] = mapped_column(
    String(20), default="available"
)  # Manual status only: maintenance, reserved. Computed: available, occupied (see SpaceService.compute_status)
```

**Note**: The `status` field is kept for future manual status support (maintenance/reserved), but is no longer written to by agreement lifecycle.

#### 1.7: Add Tests

**File**: `backend/tests/test_space_status.py` (new)

```python
@pytest.mark.asyncio
async def test_future_agreement_space_available(auth_client, site_id):
    """Space with future agreement should show as available."""
    # Create space
    space_resp = await auth_client.post(
        "/api/v1/spaces",
        json={"site_id": site_id, "name": "A-01"}
    )
    space_id = space_resp.json()["id"]

    # Create customer
    cust_resp = await auth_client.post(
        "/api/v1/customers",
        json={"name": "王小明", "phone": "0912345678"}
    )
    customer_id = cust_resp.json()["id"]

    # Create future agreement (starts tomorrow)
    from datetime import date, timedelta
    tomorrow = date.today() + timedelta(days=1)

    await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": str(tomorrow),
            "price": 3600,
            "license_plates": ["ABC-1234"],
        }
    )

    # Get space - should still be available
    space_resp = await auth_client.get(f"/api/v1/spaces/{space_id}")
    assert space_resp.status_code == 200
    data = space_resp.json()
    assert data["computed_status"] == "available"
    assert data["active_agreement_id"] is None


@pytest.mark.asyncio
async def test_active_agreement_space_occupied(auth_client, site_id):
    """Space with active agreement (start_date <= today <= end_date) should show as occupied."""
    # Similar setup...
    yesterday = date.today() - timedelta(days=1)

    # Create agreement that started yesterday
    await auth_client.post(
        "/api/v1/agreements",
        json={
            # start_date: yesterday
        }
    )

    # Get space - should be occupied
    space_resp = await auth_client.get(f"/api/v1/spaces/{space_id}")
    data = space_resp.json()
    assert data["computed_status"] == "occupied"
    assert data["active_agreement_id"] is not None


@pytest.mark.asyncio
async def test_terminated_agreement_space_available(auth_client, ...):
    """Space with terminated agreement should show as available."""
    # Create active agreement, then terminate it
    # Space should become available


@pytest.mark.asyncio
async def test_expired_agreement_space_available(auth_client, ...):
    """Space with expired agreement (end_date in past) should show as available."""
    # Create agreement with end_date in the past
    # Space should be available
```

#### 1.8: Update Existing Tests

**Files**: `backend/tests/test_agreements.py`, `backend/tests/test_spaces.py`

- Remove assertions that check `space.status == "occupied"` after agreement creation
- Replace with `computed_status` checks where appropriate

---

### Phase 2: Frontend - Display Computed Status & Agreement Link

#### 2.1: Update Space Type

**File**: `frontend/src/lib/types.ts`

```typescript
export interface Space {
  // ... existing fields ...
  computed_status: "available" | "occupied" | null;
  active_agreement_id: string | null;
}
```

#### 2.2: Update Space List Page

**File**: `frontend/src/app/(dashboard)/spaces/page.tsx`

**Option A: Add agreement link in status column**

```tsx
<TableCell>
  <div className="flex items-center gap-2">
    <Badge variant={statusColor[s.computed_status] || "default"}>
      {spaceStatusLabel(s.computed_status)}
    </Badge>
    {s.active_agreement_id && (
      <Link
        href={`/agreements/${s.active_agreement_id}`}
        className="text-xs text-blue-600 hover:underline"
      >
        查看合約
      </Link>
    )}
  </div>
</TableCell>
```

**Option B: Add separate "當前合約" column**

Add new column after status:
```tsx
<TableHead>當前合約</TableHead>
// ...
<TableCell>
  {s.active_agreement_id ? (
    <Link
      href={`/agreements/${s.active_agreement_id}`}
      className="text-blue-600 hover:underline flex items-center gap-1"
    >
      <span>查看</span>
      <ExternalLinkIcon className="h-3 w-3" />
    </Link>
  ) : (
    <span className="text-muted-foreground">-</span>
  )}
</TableCell>
```

**Recommendation**: Option A (cleaner, less columns)

#### 2.3: Update Space Edit Dialog

Show warning if trying to edit a space with an active agreement:

```tsx
{editing && editing.computed_status === "occupied" && (
  <Alert variant="warning">
    <AlertCircle className="h-4 w-4" />
    <AlertTitle>此車位有進行中的合約</AlertTitle>
    <AlertDescription>
      {editing.active_agreement_id && (
        <>
          修改前請先查看{" "}
          <Link
            href={`/agreements/${editing.active_agreement_id}`}
            className="underline"
          >
            當前合約
          </Link>
        </>
      )}
    </AlertDescription>
  </Alert>
)}
```

#### 2.4: Update Space Filter

Change "狀態" filter to use computed_status:
- Current: filters by stored `status` field
- New: filters by `computed_status` field

---

### Phase 3: Data Migration (Optional)

Since we're keeping the `status` field but no longer writing to it from agreement lifecycle, existing data may have stale values.

**Options**:

1. **Do nothing**: Frontend uses `computed_status`, old `status` field is ignored until Phase 2 (manual status)
2. **One-time migration**: Reset all `status` values to `"available"` (they'll be overridden by `computed_status` on frontend anyway)

**Recommendation**: Option 1 (do nothing). The old `status` field becomes reserved for future manual status feature.

---

## Implementation Order

### Backend First (maintains API compatibility)
1. Add `compute_status()` and `get_active_agreement()` helpers to `SpaceService`
2. Update `SpaceResponse` schema with new fields
3. Update all space API endpoints to compute status
4. Remove status mutations from `AgreementService.create()` and `terminate()`
5. Write tests for computed status logic
6. Update existing tests

### Frontend Second
7. Update `Space` type with new fields
8. Update space list to show computed_status and agreement links
9. Update filters to use computed_status
10. Add warning in edit dialog for occupied spaces

### Testing & Validation
11. Manual E2E test: Create future agreement → verify space shows available
12. Manual E2E test: Wait for agreement to become active → verify space shows occupied
13. Manual E2E test: Terminate agreement → verify space shows available
14. Manual E2E test: Click agreement link from space list → verify navigates correctly

---

## Edge Cases to Handle

1. **Multiple overlapping agreements** (shouldn't happen due to double-booking check, but defensive):
   - `get_active_agreement()` uses `.limit(1)` - returns first match
   - Consider adding `.order_by(Agreement.start_date.desc())` to get most recent

2. **Agreement spans midnight** (start_date = today):
   - SQL: `start_date <= today` (inclusive) - handles this correctly

3. **Performance with many spaces**:
   - Current approach: N+1 query (compute status for each space)
   - Optimization: Single query with subquery/join to compute all statuses at once
   - Defer optimization until profiling shows it's needed

4. **Time zone issues**:
   - Using `date.today()` which uses server timezone
   - Parking operations are local (Taiwan), so this is correct
   - No UTC conversion needed for date-only comparisons

5. **Agreement deleted** (currently not supported):
   - Agreements are immutable (no delete, only terminate)
   - If delete is added later, computed status automatically handles it

---

## Rollback Plan

If issues are discovered in production:

1. **Immediate rollback**: Revert agreement service changes, restore status mutations
2. **Frontend**: Falls back to using `status` field (add `|| s.status` fallback)
3. **Root cause**: Debug computed status logic with test data
4. **Re-deploy**: Fix and redeploy with additional tests

---

## Future Enhancements (Phase 2)

1. **Manual status support**: Add `manual_status` field to `Space` model
   - Priority: `manual_status` (if set) > `computed_status`
   - Use cases: maintenance, reserved (blocks new agreements)

2. **Status history tracking**: Log status changes to `system_logs`
   - Useful for debugging and auditing

3. **Agreement status badges**: Show pending/active/expired on agreement list
   - Already partially implemented (see `US-AGREE-006`)

4. **Space availability calendar**: Visual timeline showing when space is available/occupied

---

## Files to Modify

### Backend
- ✏️ `backend/app/services/space_service.py` - Add compute_status(), get_active_agreement()
- ✏️ `backend/app/schemas/space.py` - Add computed_status, active_agreement_id to SpaceResponse
- ✏️ `backend/app/api/spaces.py` - Update all routes to compute status
- ✏️ `backend/app/services/agreement_service.py` - Remove status mutations (lines 130-131, 169-175)
- ✏️ `backend/app/models/space.py` - Update status field comment
- ✅ `backend/tests/test_space_status.py` - New test file
- ✏️ `backend/tests/test_agreements.py` - Update tests
- ✏️ `backend/tests/test_spaces.py` - Update tests

### Frontend
- ✏️ `frontend/src/lib/types.ts` - Add fields to Space interface
- ✏️ `frontend/src/app/(dashboard)/spaces/page.tsx` - Display computed_status, agreement links

### Total: 9 files modified, 1 new file

---

## Success Criteria

- [ ] Creating a future agreement does NOT set space to occupied
- [ ] Space shows as occupied only when current_date is within agreement dates
- [ ] Terminated agreement releases space immediately
- [ ] Expired agreement (end_date in past) shows space as available
- [ ] Agreement link appears in space list when space is occupied
- [ ] Clicking link navigates to agreement detail page
- [ ] All 78 existing tests pass
- [ ] New computed status tests pass (4 new test cases)
- [ ] Frontend displays computed status correctly
- [ ] No performance degradation on space list page

---

## Estimated Effort

- Backend implementation: 3-4 hours
- Backend tests: 2 hours
- Frontend implementation: 1-2 hours
- Testing & validation: 1 hour
- **Total: 7-9 hours**
