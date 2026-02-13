# US-SPACE-004: Tag Management (CRUD)

**Priority**: Must Have | **Phase**: Phase 1 | **Sprint**: Sprint 1 (Weeks 1-2)
**Domain**: Space Management | **Epic**: Space Configuration

## User Story
As a parking lot admin, I want to create, edit, and delete tags with custom colors and optional pricing, so that I can flexibly categorize and price parking spaces.

## Acceptance Criteria

### Create Tag
- **AC1**: Admin navigates to `/admin/settings/tags` → Clicks "新增標籤" → Modal with form fields
- **AC2**: Required fields: 標籤名稱* (name), 顏色* (color picker), 說明 (description)
- **AC3**: Optional pricing fields: Checkbox "此標籤設定價格" → if checked, 月租價格* and 日租價格* become required
- **AC4**: Name validation: 2-20 characters, unique (error: "此標籤名稱已存在")
- **AC5**: Color: Hex color code from predefined palette or custom input (e.g., #FF5733)
- **AC6**: On save → Tag created, toast: "標籤已建立", logged to system_logs

### View Tag List
- **AC7**: Tag list page displays table with columns: 顏色, 名稱, 說明, 月租價格, 日租價格, 使用數量, 操作
- **AC8**: Each row shows: color dot, name, description (truncated), prices (or "無" if no price), count of spaces using this tag, edit/delete actions
- **AC9**: Tags sorted alphabetically by name

### Edit Tag
- **AC10**: Admin clicks "編輯" on a tag → Modal pre-filled with current values
- **AC11**: Editable fields: name, color, description, pricing toggle + prices
- **AC12**: If tag has price and admin changes it → Warning: "此標籤目前已應用於 X 個車位，價格變更不會自動更新現有車位。如需更新價格，請移除後重新加入標籤。"
- **AC13**: Changing tag name → All spaces referencing this tag by name in their tags[] array are auto-updated
- **AC14**: On save → Tag updated, toast: "標籤已更新", logged to system_logs

### Delete Tag
- **AC15**: Admin clicks "刪除" on a tag → Confirmation: "確定要刪除標籤「有屋頂」嗎？"
- **AC16**: Tag deletion does NOT affect space data:
  - Space tags[] array: Tag name removed from array
  - Space price: Unchanged (even if tag had pricing)
  - Space price_source: If was 'tag' referencing this tag, changes to 'custom' (preserves current price)
- **AC17**: On delete → Tag removed, spaces updated, toast: "標籤已刪除", logged to system_logs
- **AC18**: Deletion is permanent (no soft delete for tags)

## Business Rules

### Tag Identity
- Tags are identified by name (unique, case-sensitive)
- Tags have no categories or hierarchy — flat list
- Tag names stored in space tags[] array as TEXT values

### Tag Colors
- Each tag has exactly one color (hex code)
- Color used for visual indicators: dots on space grids, badges in lists
- No uniqueness constraint on colors (multiple tags can share a color)
- Predefined palette of 12-16 common colors for quick selection, plus custom hex input

### Tag Pricing (Optional)
- Tags may optionally define monthly and daily prices
- Both monthly AND daily prices required if pricing is enabled (cannot set just one)
- Tag price behavior on spaces: see US-SPACE-003 for complete pricing rules
- Changing tag price does NOT auto-update spaces already tagged (prevents unexpected bulk changes)

### Tag Deletion Impact
- Space tags[] array: tag name removed automatically
- Space pricing: price remains unchanged (does NOT revert)
- Space price_source: if 'tag' → changes to 'custom' (preserves the price that was set by the tag)
- price_source_tag_id: set to NULL
- Agreements: completely unaffected (price is immutable snapshot)
- Audit logs: tag deletion logged, space updates logged individually

### Tag Usage
- Tags are for flexible categorization (e.g., "有屋頂", "VIP", "大車位", "角落位")
- Also used for bulk pricing: "有屋頂" spaces cost more
- Multiple tags per space allowed
- Tag order in array not significant

## UI Requirements

### Tag Settings Page
**Location**: `/admin/settings/tags`

**Page Structure**:
1. Page header: "標籤管理" + "新增標籤" button
2. Tag table

**Table Columns**:
| 顏色 | 名稱 | 說明 | 月租價格 | 日租價格 | 使用數量 | 操作 |
|------|------|------|---------|---------|---------|------|
| [dot] | 有屋頂 | 有屋頂遮蔽的車位 | NT$4,000 | NT$180 | 12 | 編輯 \| 刪除 |
| [dot] | VIP | VIP 客戶專用車位 | NT$5,000 | NT$220 | 5 | 編輯 \| 刪除 |
| [dot] | 大車位 | 可停大型車輛 | 無 | 無 | 8 | 編輯 \| 刪除 |

### Create/Edit Tag Modal
**Fields**:
- **標籤名稱 * (Tag Name)**:
  - Type: Text input
  - Placeholder: "例如：有屋頂"
  - Validation: Required, 2-20 chars, unique

- **顏色 * (Color)**:
  - Type: Color picker with predefined palette
  - Palette: 12-16 colors (red, orange, yellow, green, teal, blue, indigo, purple, pink, brown, gray, black)
  - Custom hex input option
  - Preview: Color dot shown next to tag name

- **說明 (Description)**:
  - Type: Textarea
  - Optional, max 200 chars
  - Placeholder: "例如：有屋頂遮蔽的車位"

- **此標籤設定價格 (Enable Pricing)** (checkbox):
  - Unchecked by default
  - If checked, show price fields:
    - **月租價格 * (Monthly Price)**: NT$ number input, required if pricing enabled
    - **日租價格 * (Daily Price)**: NT$ number input, required if pricing enabled

**Actions**: "儲存" (primary) | "取消" (secondary)

### Delete Confirmation
**Dialog**: "確定要刪除標籤「{name}」嗎？此標籤將從 {count} 個車位中移除，但車位價格不會改變。"
**Actions**: "確定刪除" (red/danger) | "取消" (secondary)

## Implementation Notes

### Database Schema

```sql
CREATE TABLE tags (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE CHECK (char_length(name) >= 2 AND char_length(name) <= 20),
  color TEXT NOT NULL CHECK (color ~ '^#[0-9A-Fa-f]{6}$'),
  description TEXT CHECK (char_length(description) <= 200),
  has_price BOOLEAN NOT NULL DEFAULT FALSE,
  monthly_price INTEGER CHECK (monthly_price >= 0),
  daily_price INTEGER CHECK (daily_price >= 0),
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  CONSTRAINT check_tag_price CHECK (
    (has_price = TRUE AND monthly_price IS NOT NULL AND daily_price IS NOT NULL)
    OR (has_price = FALSE AND monthly_price IS NULL AND daily_price IS NULL)
  )
);
```

### Tag Deletion Cleanup
```typescript
async function deleteTag(tagId: string) {
  const tag = await getTag(tagId);

  // Remove tag name from all spaces' tags[] array
  await db.query(`
    UPDATE spaces
    SET tags = array_remove(tags, $1),
        price_source = CASE
          WHEN price_source_tag_id = $2 THEN 'custom'
          ELSE price_source
        END,
        price_source_tag_id = CASE
          WHEN price_source_tag_id = $2 THEN NULL
          ELSE price_source_tag_id
        END,
        updated_at = now()
    WHERE $1 = ANY(tags)
  `, [tag.name, tagId]);

  // Delete the tag
  await db.tags.delete(tagId);

  // Log deletion
  await logToAudit('DELETE_TAG', {
    tag_id: tagId,
    old_values: { name: tag.name, color: tag.color }
  });
}
```

### Tag Name Rename Propagation
```typescript
async function renameTag(tagId: string, oldName: string, newName: string) {
  // Update tag record
  await db.tags.update(tagId, { name: newName });

  // Update all spaces' tags[] arrays
  await db.query(`
    UPDATE spaces
    SET tags = array_replace(tags, $1, $2),
        updated_at = now()
    WHERE $1 = ANY(tags)
  `, [oldName, newName]);
}
```

## Source
init_draft.md line 24 (tag system), CLAUDE.md (tag architecture)

## Dependencies
- US-SPACE-003 (pricing model — tag pricing integration)
- US-AUDIT-002 (audit logging)
- US-LOC-003 (TWD currency format)

## Test Data

### Tags
**Tag 1 - 有屋頂** (with price):
- Color: #2196F3 (blue)
- Description: 有屋頂遮蔽的車位
- Monthly price: NT$4,000
- Daily price: NT$180
- Usage: 12 spaces

**Tag 2 - VIP** (with price):
- Color: #FFD700 (gold)
- Description: VIP 客戶專用車位
- Monthly price: NT$5,000
- Daily price: NT$220
- Usage: 5 spaces

**Tag 3 - 大車位** (no price):
- Color: #4CAF50 (green)
- Description: 可停大型車輛
- Monthly price: 無
- Daily price: 無
- Usage: 8 spaces

**Tag 4 - 角落位** (no price):
- Color: #9E9E9E (gray)
- Description: 角落位置
- Monthly price: 無
- Daily price: 無
- Usage: 4 spaces

### Tag Deletion Scenario
**Delete "有屋頂" tag**:
1. Before: Space A-02 has tags=['有屋頂', '大車位'], price_source='tag', monthly=4000
2. Delete "有屋頂" tag
3. After: Space A-02 has tags=['大車位'], price_source='custom', monthly=4000 (unchanged)

### Tag Rename Scenario
**Rename "VIP" → "VIP客戶"**:
1. Before: Space A-05 has tags=['VIP']
2. Rename tag
3. After: Space A-05 has tags=['VIP客戶'] (auto-updated)

### Validation Errors
- Empty name: "標籤名稱為必填欄位"
- Duplicate name: "此標籤名稱已存在"
- Name too short: "標籤名稱至少 2 個字元"
- Invalid color: "請選擇有效的顏色"
- Pricing enabled but no monthly: "啟用價格時月租價格為必填"
- Pricing enabled but no daily: "啟用價格時日租價格為必填"
