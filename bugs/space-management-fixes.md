# Space Management - Bugs & Missing Features

5 issues identified from manual testing. Each has a detailed design and execution plan.

---

## Bug #1: Space Name Should Be Unique (Per Site)

### Problem
Space names have no uniqueness constraint. Users can create duplicate names within the same site (e.g., two "A-01" in the same parking lot), causing confusion.

**Contrast**: Sites and Tags already enforce `unique=True` on name.

### Design

**Scope**: Per-site uniqueness. Two different sites CAN have the same space name (e.g., Site A has "A-01" and Site B also has "A-01").

#### Backend Changes

1. **Model** (`backend/app/models/space.py`):
   - Add `UniqueConstraint("site_id", "name", name="uq_space_site_name")` to `__table_args__`

2. **Migration**:
   - `alembic revision --autogenerate -m "add unique constraint on space site_id+name"`
   - Before running: verify no existing duplicate data in production

3. **Service** (`backend/app/services/space_service.py`):
   - In `create()`: query for existing space with same `(site_id, name)` before insert
   - Raise `DuplicateError("車位", "名稱")` if exists (returns 409)
   - In `update()`: if `name` is being changed, check uniqueness against same site
   - Note: `DuplicateError` already exists in `app/utils/errors.py` with 409 handler in `main.py`

4. **Tests** (`backend/tests/test_spaces.py`):
   - Test: create duplicate name in same site -> 409
   - Test: create same name in different site -> 201 (allowed)
   - Test: rename space to existing name in same site -> 409

#### Frontend Changes

5. **Space list page** (`frontend/src/app/(dashboard)/spaces/page.tsx`):
   - No UI changes needed - backend 409 error will be caught by `ApiError` handler and shown as toast

### Execution Order
1. Backend model + migration
2. Backend service validation
3. Backend tests
4. Manual verify frontend toast on duplicate

---

## Bug #2: Batch Create Space Flow

### Problem
No way to create multiple spaces at once. Parking lots have ~30-40 spaces each; creating one-by-one is tedious. Space naming should follow a sequential pattern like `{prefix}-{number}`.

### Design

**UX**: User selects a site, enters a prefix (e.g., "A"), a start number (e.g., 1), and a count (e.g., 10). System creates A-01, A-02, ... A-10. If any conflicts exist (e.g., A-03 already exists), the request fails with a clear error listing the conflicting names.

**Naming format**: `{prefix}-{number}` where number is zero-padded to 2 digits (01-99). If count would exceed 99, pad to 3 digits (001-999).

#### Backend Changes

1. **Schema** (`backend/app/schemas/space.py`):
   - Add `SpaceBatchCreate` model:
     ```python
     class SpaceBatchCreate(BaseModel):
         site_id: UUID
         prefix: str = Field(..., min_length=1, max_length=20, pattern=r"^[A-Za-z0-9\u4e00-\u9fff]+$")
         start: int = Field(..., ge=1, le=999)
         count: int = Field(..., ge=1, le=100)
     ```

2. **Service** (`backend/app/services/space_service.py`):
   - Add `batch_create(data: SpaceBatchCreate) -> list[Space]` method:
     - Generate names: `{prefix}-{start:02d}` through `{prefix}-{start+count-1:02d}`
     - Query all existing space names for the site
     - If any generated name conflicts, raise `BusinessError` listing conflicts (e.g., "以下車位名稱已存在：A-03, A-05")
     - If no conflicts, bulk insert all spaces
     - Single audit log entry with `action="BATCH_CREATE"` and all names in `new_values`

3. **API** (`backend/app/api/spaces.py`):
   - Add `POST /api/v1/spaces/batch` endpoint
   - Returns `201` with list of created spaces

4. **Tests**:
   - Test: batch create 5 spaces -> 201, names correct
   - Test: batch create with conflict -> 400, lists conflicts
   - Test: batch create with start=5, count=3 -> A-05, A-06, A-07
   - Test: prefix validation (no special chars)
   - Test: count limit (max 100)

#### Frontend Changes

5. **Space list page** (`frontend/src/app/(dashboard)/spaces/page.tsx`):
   - Add "批次新增" (Batch Create) button next to existing "新增車位" button
   - New dialog with fields:
     - 停車場 (Site): Select dropdown (required)
     - 前綴 (Prefix): Text input, e.g., "A" (required)
     - 起始編號 (Start Number): Number input, default 1 (required)
     - 數量 (Count): Number input, default 10 (required)
   - Preview section showing generated names before submit (e.g., "將建立：A-01, A-02, ..., A-10")
   - Success toast: "已新增 10 個車位"
   - Error toast: shows backend conflict message

### Execution Order
1. Backend schema
2. Backend service method
3. Backend API endpoint
4. Backend tests
5. Frontend batch create dialog

---

## Bug #3: Tag Colors Missing in Space List

### Problem
Tags displayed on the space list page are plain text badges with no color. The tag color data exists in the database and is already loaded on the page (via `tags` state), but not used when rendering space tags.

### Design

**Fix**: Look up tag color from the loaded `tags` array and apply it as a colored dot or badge background.

#### Frontend Changes (Only)

1. **Space list page** (`frontend/src/app/(dashboard)/spaces/page.tsx`):
   - Build a `tagColorMap` from loaded `tags`: `Record<string, string>` mapping tag name to color
   - Replace plain `<Badge variant="outline">{tag}</Badge>` with a badge that includes a color dot:
     ```tsx
     <Badge variant="outline" className="flex items-center gap-1">
       <span
         className="inline-block h-2.5 w-2.5 rounded-full"
         style={{ backgroundColor: tagColorMap[tag] || "#6B7280" }}
       />
       {tag}
     </Badge>
     ```
   - This matches the pattern used on the tags management page

2. **Also add colors to the tag filter dropdown** (lines 157-167):
   - Add color dot before tag name in `SelectItem` for visual consistency

No backend changes needed. No tests needed (visual-only change).

### Execution Order
1. Build tag color map from existing state
2. Update tag badges in table
3. Update tag filter dropdown
4. Manual visual verification

---

## Bug #4: Missing Workflow to Add/Remove Tags from a Space

### Problem
There is no UI to add or remove tags from a space. The space list only shows tags read-only. The backend `SpaceUpdate` schema already supports updating `tags`, but there's no frontend to use it.

### Design

**UX**: Add an "Edit" button (編輯) per space row. Clicking opens a dialog pre-filled with the space's current data. The dialog includes a multi-select for tags (checkboxes), status dropdown, and custom price field (see Bug #5). This single dialog covers Bugs #4 and #5.

#### Frontend Changes

1. **Space list page** (`frontend/src/app/(dashboard)/spaces/page.tsx`):

   - **Add "操作" (Actions) column** to the table with "編輯" and "刪除" buttons per row (consistent with tags/sites pages)

   - **Add edit state**: `editing: Space | null`, set when clicking "編輯"

   - **Add edit dialog** with fields:
     - 車位名稱 (Name): Text input, pre-filled
     - 狀態 (Status): Select dropdown (available/occupied/reserved/maintenance)
     - 標籤 (Tags): Multi-select checkboxes from loaded `tags` list, with color dots
     - 自訂月租價格 (Custom Monthly Price): Number input, optional (see Bug #5)

   - **Tag multi-select UI**:
     - Show all available tags as checkboxes with color dots
     - Pre-check tags that the space currently has
     - On save, send updated `tags` array via `PUT /api/v1/spaces/{id}`

   - **Delete button**: Confirmation dialog, calls `DELETE /api/v1/spaces/{id}`
     - Error toast if space has active agreements (backend returns 400)

2. **API calls**:
   - Edit: `api.put(`/api/v1/spaces/${space.id}`, { tags, status, name, custom_price })`
   - Delete: `api.delete(`/api/v1/spaces/${space.id}`)`

No backend changes needed - `SpaceUpdate` schema and `PUT` endpoint already support `tags` field.

### Execution Order
1. Add actions column with edit/delete buttons
2. Build edit dialog with tag multi-select
3. Wire up PUT API call
4. Add delete with confirmation
5. Manual test: add tag, remove tag, verify pricing updates

---

## Bug #5: Missing Workflow to Edit Space Price

### Problem
There's no UI to set or edit a space's `custom_price`. The three-tier pricing model exists in the backend but is read-only on the frontend. Additionally, the current priority (Tag > Custom > Site) needs to be changed to **Custom > Tag > Site** so that manual overrides always take effect.

### Design

#### Pricing Priority Change

**New priority**: Custom > Tag > Site (per user decision)

This means: if an admin explicitly sets a custom price on a space, it overrides everything, including tag-based pricing. This makes the "manual override" truly an override.

#### Backend Changes

1. **Pricing utility** (`backend/app/utils/pricing.py`):
   - Change computation order:
     ```python
     # Start with site base price
     tier = "site"

     # Tag price overrides site base
     if tags:
         # ... find first priced tag, set tier = "tag"

     # Custom price has HIGHEST priority — overrides both site and tag
     if custom_price is not None:
         monthly = custom_price
         tier = "custom"
     ```
   - Daily price: custom_price only sets monthly. Daily price follows: tag daily > site daily (custom_price is monthly-only per existing schema)

2. **Tests** (`backend/tests/test_pricing.py`):
   - Update test case "tag overrides custom" -> now custom overrides tag
   - Add test: custom_price set + priced tag -> custom wins
   - Add test: custom_price cleared (None) + priced tag -> tag wins
   - Verify all 9 existing test scenarios still make sense

3. **Schema docs**: Update `SpaceResponse` field comment for `price_tier` to reflect new priority

#### Frontend Changes (Part of Bug #4 Edit Dialog)

4. **Edit dialog** (same dialog as Bug #4):
   - **自訂月租價格 (Custom Monthly Price)** field:
     - Number input, optional, min=0
     - Placeholder showing current effective price (e.g., "目前：NT$3,600 (來自場地)")
     - Clear button to remove custom price (set to `null`)
     - Help text: "設定後將覆蓋標籤和場地價格" (After setting, overrides tag and site prices)

   - **Price preview**: After changing custom_price or tags, show what the new effective price will be

5. **Space list display** remains the same - shows effective_monthly_price and price_tier badge

### Execution Order
1. Backend: update pricing.py priority logic
2. Backend: update/add pricing tests
3. Frontend: add custom_price field to edit dialog (combined with Bug #4)
4. Manual test: set custom price, verify it overrides tag price

---

## Implementation Summary

### Combined Execution Plan

| Phase | Items | Estimated Scope |
|-------|-------|----------------|
| 1 | Bug #1: Unique constraint + service validation | Backend: model, migration, service, tests |
| 2 | Bug #2: Batch create | Backend: schema, service, API, tests + Frontend: dialog |
| 3 | Bug #5 (backend): Pricing priority change | Backend: pricing.py, tests |
| 4 | Bug #3: Tag colors in space list | Frontend only |
| 5 | Bug #4 + #5 (frontend): Edit dialog with tags + price | Frontend: edit dialog, delete, multi-select |

### Files to Modify

**Backend**:
- `backend/app/models/space.py` - Add unique constraint
- `backend/app/schemas/space.py` - Add SpaceBatchCreate
- `backend/app/services/space_service.py` - Add duplicate check, batch_create
- `backend/app/api/spaces.py` - Add batch endpoint
- `backend/app/utils/pricing.py` - Change priority order
- `backend/tests/test_spaces.py` - Add uniqueness + batch tests
- `backend/tests/test_pricing.py` - Update priority tests
- New Alembic migration

**Frontend**:
- `frontend/src/app/(dashboard)/spaces/page.tsx` - All UI changes (tag colors, edit dialog, batch dialog, delete)

### Dependencies
- Bug #3 has no dependencies (can be done first or in parallel)
- Bug #4 and #5 frontend share the same edit dialog (do together)
- Bug #5 backend (pricing change) should be done before Bug #5 frontend
- Bug #1 must be done before Bug #2 (batch create relies on uniqueness validation)
