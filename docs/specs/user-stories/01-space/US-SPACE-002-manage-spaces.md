# US-SPACE-002: Create/Edit/Delete Spaces

**Priority**: Must Have | **Phase**: Phase 1 | **Sprint**: Sprint 1 (Weeks 1-2)
**Domain**: Space Management | **Epic**: Space Configuration

## User Story
As a parking lot admin, I want to create, edit, and delete parking spaces with enforced naming conventions and bulk creation support, so that I can efficiently manage my parking inventory.

## Acceptance Criteria

### Create Single Space
- **AC1**: Admin navigates to space management → Clicks "新增車位" → Modal with form fields
- **AC2**: Required fields: 停車場* (site dropdown), 車位編號* (auto-suggested), 標籤 (multi-select tags)
- **AC3**: Space name enforced format: `{site_prefix}-{number}` where number is zero-padded 2 digits (e.g., A-01, A-02, B-15)
- **AC4**: Auto-suggest next available number for selected site (e.g., if A-01 through A-10 exist, suggest A-11)
- **AC5**: Name must be unique within the site (error: "車位 A-11 已存在")
- **AC6**: Space inherits site base price on creation (monthly_price, daily_price, price_source='site_base')
- **AC7**: On save → Space created, toast: "車位已建立", logged to system_logs

### Bulk Space Creation
- **AC8**: Admin clicks "批次新增" → Modal with fields: 停車場* (site dropdown), 前綴* (prefix), 起始編號* (start number), 數量* (count)
- **AC9**: Sequential naming: `{prefix}-{number}` where number is zero-padded to 2 digits (01-99), or 3 digits if count exceeds 99
- **AC10**: Prefix validation: 1-20 characters, alphanumeric + Chinese only (pattern: `^[A-Za-z0-9\u4e00-\u9fff]+$`)
- **AC11**: Preview section shows generated names before submit (e.g., "將建立：A-01, A-02, ..., A-10")
- **AC12**: Validation: if ANY generated name conflicts with existing space in same site → Request fails with error listing all conflicts (e.g., "以下車位名稱已存在：A-03, A-05")
- **AC13**: Max bulk creation: 100 spaces per batch
- **AC14**: All spaces inherit site base price
- **AC15**: On success → All spaces created in single transaction, toast: "已新增 10 個車位", single audit log entry with action="BATCH_CREATE"
- **AC16**: On conflict error → No spaces created (atomic operation), show error toast with conflicting names

### Edit Space
- **AC17**: Admin clicks "編輯" button in space row actions → Edit modal with current values
- **AC18**: Editable fields:
  - 車位名稱 (read-only display)
  - 狀態 (status dropdown: available/occupied/reserved/maintenance)
  - 標籤 (multi-select checkboxes with color dots)
  - 自訂月租價格 (custom monthly price, optional number input with clear button)
  - 備註 (notes)
- **AC19**: Space name and site are NOT editable after creation (references depend on it)
- **AC20**: Tag multi-select UI shows all available tags as checkboxes with color dots, pre-checked tags that space currently has
- **AC21**: Custom price field shows placeholder with current effective price and source (e.g., "目前：NT$3,600 (來自場地)")
- **AC22**: Help text for custom price: "設定後將覆蓋標籤和場地價格"
- **AC23**: On save → Space updated, toast: "車位已更新", logged to system_logs

### Delete Space
- **AC24**: Admin clicks "刪除" button in space row actions → Confirmation dialog: "確定要刪除車位 A-05 嗎？此操作無法復原。"
- **AC25**: Deletion blocked if space has any active agreements (error: "車位 A-05 有活躍合約，無法刪除")
- **AC26**: Deletion allowed only for spaces with zero agreements OR only terminated/expired agreements
- **AC27**: On delete → Space permanently removed, toast: "車位已刪除", logged to system_logs
- **AC28**: Deleted space number becomes available for reuse

### Space from Deactivated Site
- **AC25**: Cannot create spaces under a deactivated site (site dropdown only shows active sites)

## Business Rules

### Naming Convention
- Format: `{site_prefix}-{zero_padded_number}` (e.g., A-01, B-15, C-03)
- Number: 01-99 range (2-digit zero-padded)
- Name is immutable after creation
- Name must be unique within the site (different sites can have same number: A-01 and B-01 are both valid)

### Bulk Creation
- Creates spaces sequentially: `{prefix}-{start:02d}` through `{prefix}-{start+count-1:02d}`
- Naming format: zero-padded to 2 digits (01-99), or 3 digits (001-999) if needed
- Prefix must match pattern: alphanumeric + Chinese characters only
- If any generated name conflicts → entire batch fails (atomic operation, no partial creation)
- Maximum 100 spaces per batch
- All spaces get identical initial configuration (site base price, no tags)
- Single audit log entry with all created space names in new_values

### Deletion Rules
- Hard delete (permanent) — not soft delete
- Only allowed when no agreements exist, OR all agreements are terminated/expired
- Active/pending agreements block deletion
- Space number freed for reuse after deletion
- Deletion is irreversible — confirm dialog required

### Initial Space Configuration
- Price: Inherited from site base price (price_source='site_base')
- Tags: Empty array (no tags by default)
- Status: Computed (available if no active agreement covers current_date)
- Manual status: NULL (not maintenance or reserved)

## UI Requirements

### Space Management Page
**Location**: `/admin/spaces` (integrated with space list from US-SPACE-005)

**Action Buttons**:
- "新增車位" → Single space creation modal
- "批量新增" → Bulk creation modal

### Single Space Creation Modal
**Fields**:
- **停車場 * (Site)**:
  - Type: Dropdown (active sites only)
  - Shows: site name + prefix (e.g., "A區停車場 (A)")

- **車位編號 * (Space Number)**:
  - Type: Number input
  - Auto-suggestion: Next available number
  - Display preview: "車位名稱: A-{input}" (live preview)
  - Validation: 1-99, unique within site

- **標籤 (Tags)**:
  - Type: Multi-select dropdown
  - Shows: tag name + color dot
  - Optional

- **備註 (Notes)**:
  - Type: Textarea
  - Optional, max 200 chars

**Actions**: "建立" (primary) | "取消" (secondary)

### Bulk Creation Modal
**Fields**:
- **停車場 * (Site)**:
  - Type: Dropdown (active sites only)

- **前綴 * (Prefix)**:
  - Type: Text input
  - Placeholder: "例如：A"
  - Validation: 1-20 chars, alphanumeric + Chinese only

- **起始編號 * (Start Number)**:
  - Type: Number input
  - Validation: 1-999
  - Default: 1

- **數量 * (Count)**:
  - Type: Number input
  - Validation: 1-100
  - Default: 10

**Preview Section** (shown after inputs filled):
- Shows generated names: "將建立：A-01, A-02, ..., A-10"
- If conflicts detected, shows error: "以下車位名稱已存在：A-03, A-05" (submit disabled)
- If no conflicts: Shows success state with total count

**Actions**: "建立" (primary, disabled if conflicts) | "取消" (secondary)

### Edit Space Modal
**Fields**:
- **車位名稱** (read-only display): A-05
- **停車場** (read-only display): A區停車場
- **狀態 (Status)**:
  - Type: Dropdown
  - Options: available/occupied/reserved/maintenance
- **標籤 (Tags)**:
  - Type: Multi-select checkboxes
  - Shows all available tags with color dots
  - Pre-check tags that space currently has
- **自訂月租價格 (Custom Monthly Price)**:
  - Type: Number input, optional, min=0
  - Placeholder: "目前：NT$3,600 (來自場地)"
  - Clear button to remove custom price (set to null)
  - Help text: "設定後將覆蓋標籤和場地價格"
- **備註 (Notes)**: Textarea, max 200 chars

**Actions**: "儲存" (primary) | "取消" (secondary)

### Delete Confirmation
**Dialog**: "確定要刪除車位 {name} 嗎？此操作無法復原。所有相關資料將被永久移除。"
**Actions**: "確定刪除" (red/danger) | "取消" (secondary)

## Implementation Notes

### Database Schema

```sql
CREATE TABLE spaces (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id UUID NOT NULL REFERENCES sites(id),
  name TEXT NOT NULL,
  tags TEXT[] DEFAULT '{}',
  custom_price INTEGER,  -- NULL means no custom override; when set, overrides tag and site prices
  monthly_price INTEGER NOT NULL,  -- Computed effective price based on priority: custom > tag > site
  daily_price INTEGER NOT NULL,
  price_source TEXT NOT NULL DEFAULT 'site_base' CHECK (price_source IN ('site_base', 'custom', 'tag')),
  price_source_tag_id UUID REFERENCES tags(id),
  manual_status TEXT CHECK (manual_status IN ('maintenance', 'reserved')),
  notes TEXT CHECK (char_length(notes) <= 200),
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(site_id, name)  -- Enforce per-site uniqueness
);

CREATE INDEX idx_spaces_site_id ON spaces(site_id);
CREATE INDEX idx_spaces_tags ON spaces USING GIN(tags);
CREATE INDEX idx_spaces_manual_status ON spaces(manual_status);
```

### Bulk Creation Logic
```typescript
async function bulkCreateSpaces(
  siteId: string,
  prefix: string,
  startNumber: number,
  count: number
) {
  const site = await getSite(siteId);

  // Generate all space names
  const maxNumber = startNumber + count - 1;
  const digits = maxNumber > 99 ? 3 : 2;
  const names: string[] = [];

  for (let i = 0; i < count; i++) {
    const number = startNumber + i;
    const name = `${prefix}-${String(number).padStart(digits, '0')}`;
    names.push(name);
  }

  // Check for conflicts
  const existing = await getExistingSpaceNames(siteId, names);
  if (existing.length > 0) {
    throw new BusinessError(`以下車位名稱已存在：${existing.join(', ')}`);
  }

  // Create all spaces in single transaction
  await db.transaction(async (trx) => {
    for (const name of names) {
      await trx.spaces.create({
        site_id: siteId,
        name,
        monthly_price: site.monthly_base_price,
        daily_price: site.daily_base_price,
        price_source: 'site_base'
      });
    }

    // Single audit log entry
    await trx.system_logs.create({
      action: 'BATCH_CREATE',
      table: 'spaces',
      new_values: { names, count: names.length }
    });
  });

  return { created: names };
}
```

### Deletion Guard
```typescript
async function canDeleteSpace(spaceId: string): Promise<boolean> {
  const activeCount = await db.agreements.count({
    space_id: spaceId,
    status: { $ne: 'terminated' },
    // Also check computed status: non-terminated AND not expired
    end_date: { $gte: new Date() }
  });
  return activeCount === 0;
}
```

## Source
init_draft.md (space creation, naming), CLAUDE.md (space management)

## Dependencies
- US-SPACE-001 (site must exist for space creation)
- US-SPACE-003 (pricing model — price inheritance)
- US-SPACE-004 (tags — tag assignment on spaces)
- US-AUDIT-002 (audit logging)

## Test Data

### Single Creation
**Create Space**:
- Site: A區停車場 (prefix: A)
- Number: 11
- Result: Space "A-11" created, price=NT$3,600/month (site base)

### Bulk Creation
**Bulk Create (Success)**:
- Site: A區停車場
- Prefix: A, Start: 5, Count: 10
- No existing conflicts
- Result: Created A-05, A-06, A-07, A-08, A-09, A-10, A-11, A-12, A-13, A-14 (10 created)

**Bulk Create (Conflict)**:
- Site: A區停車場
- Prefix: A, Start: 1, Count: 10
- Existing: A-03, A-05
- Result: Error "以下車位名稱已存在：A-03, A-05", no spaces created

### Validation Errors
- Duplicate number: "車位 A-01 已存在"
- Number out of range: "車位編號須為 1-999"
- Invalid prefix: "前綴只能包含英文、數字和中文"
- Bulk count too large: "批量新增上限為 100 個車位"
- Bulk conflict: "以下車位名稱已存在：A-03, A-05"
- Delete blocked: "車位 A-05 有活躍合約，無法刪除"

### Delete Scenarios
**Can delete**: A-14 has zero agreements → Deletion succeeds
**Cannot delete**: A-01 has 1 active agreement → "車位 A-01 有 1 份合約記錄，無法刪除"
**Can delete**: A-03 has 2 terminated agreements only → Deletion succeeds (only non-terminated block)
