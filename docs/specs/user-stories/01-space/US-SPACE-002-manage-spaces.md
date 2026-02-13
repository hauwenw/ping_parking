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
- **AC8**: Admin clicks "批量新增" → Modal with fields: 停車場* (site dropdown), 起始編號* (start number), 數量* (count)
- **AC9**: Sequential naming from start number: e.g., Site A, start=5, count=10 → Creates A-05 through A-14
- **AC10**: Validation: skip numbers that already exist (show warning: "以下編號已存在將跳過：A-07, A-09")
- **AC11**: Max bulk creation: 50 spaces per batch
- **AC12**: All spaces inherit site base price
- **AC13**: Progress indicator during bulk creation, success: "已成功建立 X 個車位 (跳過 Y 個重複編號)"
- **AC14**: All creations logged individually to system_logs

### Edit Space
- **AC15**: Admin clicks space row → Edit modal with current values
- **AC16**: Editable fields: 標籤 (multi-select tags), 自訂價格 (custom price override), 備註 (notes)
- **AC17**: Space name is NOT editable after creation (references depend on it)
- **AC18**: Tag changes: adding/removing tags follows pricing rules per US-SPACE-003
- **AC19**: On save → Space updated, toast: "車位已更新", logged to system_logs

### Delete Space
- **AC20**: Admin clicks "刪除" on a space → Confirmation: "確定要刪除車位 A-05 嗎？此操作無法復原。"
- **AC21**: Deletion blocked if space has any non-terminated agreements (error: "車位 A-05 有 X 份合約記錄，無法刪除")
- **AC22**: Deletion allowed only for spaces with zero agreements OR only terminated/expired agreements
- **AC23**: On delete → Space permanently removed, toast: "車位已刪除", logged to system_logs
- **AC24**: Deleted space number becomes available for reuse

### Space from Deactivated Site
- **AC25**: Cannot create spaces under a deactivated site (site dropdown only shows active sites)

## Business Rules

### Naming Convention
- Format: `{site_prefix}-{zero_padded_number}` (e.g., A-01, B-15, C-03)
- Number: 01-99 range (2-digit zero-padded)
- Name is immutable after creation
- Name must be unique within the site (different sites can have same number: A-01 and B-01 are both valid)

### Bulk Creation
- Creates spaces sequentially: start_number to start_number + count - 1
- Skips existing numbers (does not error, just warns)
- Maximum 50 spaces per batch to prevent accidental mass creation
- All spaces get identical initial configuration (site base price, no tags)

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

- **起始編號 * (Start Number)**:
  - Type: Number input
  - Validation: 1-99

- **數量 * (Count)**:
  - Type: Number input
  - Validation: 1-50
  - Preview: "將建立 A-05 至 A-14 (共 10 個車位)"

**Preview Section** (shown after inputs filled):
- List of space names to be created
- Highlight conflicts: "A-07 (已存在，將跳過)" in yellow
- Total: "將建立 8 個新車位 (跳過 2 個)"

**Actions**: "建立" (primary) | "取消" (secondary)

### Edit Space Modal
**Fields**:
- **車位名稱** (read-only display): A-05
- **停車場** (read-only display): A區停車場
- **標籤**: Multi-select dropdown
- **價格**: See US-SPACE-003 for custom price override UI
- **備註**: Textarea

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
  monthly_price INTEGER NOT NULL,
  daily_price INTEGER NOT NULL,
  price_source TEXT NOT NULL DEFAULT 'site_base' CHECK (price_source IN ('site_base', 'custom', 'tag')),
  price_source_tag_id UUID REFERENCES tags(id),
  manual_status TEXT CHECK (manual_status IN ('maintenance', 'reserved')),
  notes TEXT CHECK (char_length(notes) <= 200),
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(site_id, name)
);

CREATE INDEX idx_spaces_site_id ON spaces(site_id);
CREATE INDEX idx_spaces_tags ON spaces USING GIN(tags);
CREATE INDEX idx_spaces_manual_status ON spaces(manual_status);
```

### Bulk Creation Logic
```typescript
async function bulkCreateSpaces(
  siteId: string,
  startNumber: number,
  count: number
) {
  const site = await getSite(siteId);
  const existing = await getSpaceNames(siteId);
  const created: string[] = [];
  const skipped: string[] = [];

  for (let i = startNumber; i < startNumber + count && i <= 99; i++) {
    const name = `${site.prefix}-${String(i).padStart(2, '0')}`;
    if (existing.includes(name)) {
      skipped.push(name);
      continue;
    }
    await createSpace({
      site_id: siteId,
      name,
      monthly_price: site.monthly_base_price,
      daily_price: site.daily_base_price,
      price_source: 'site_base'
    });
    created.push(name);
  }

  return { created, skipped };
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
**Bulk Create**:
- Site: A區停車場 (prefix: A)
- Start: 5, Count: 10
- Existing: A-07, A-09
- Result: Created A-05, A-06, A-08, A-10, A-11, A-12, A-13, A-14 (8 created, 2 skipped)

### Validation Errors
- Duplicate number: "車位 A-01 已存在"
- Number out of range: "車位編號須為 1-99"
- Bulk count too large: "批量新增上限為 50 個車位"
- Delete blocked: "車位 A-05 有 2 份合約記錄，無法刪除"

### Delete Scenarios
**Can delete**: A-14 has zero agreements → Deletion succeeds
**Cannot delete**: A-01 has 1 active agreement → "車位 A-01 有 1 份合約記錄，無法刪除"
**Can delete**: A-03 has 2 terminated agreements only → Deletion succeeds (only non-terminated block)
