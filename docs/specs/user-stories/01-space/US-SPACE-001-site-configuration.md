# US-SPACE-001: Site Configuration (CRUD)

**Priority**: Must Have | **Phase**: Phase 1 | **Sprint**: Sprint 1 (Weeks 1-2)
**Domain**: Space Management | **Epic**: Space Configuration

## User Story
As a parking lot admin, I want to create, view, edit, and deactivate parking sites with address and naming prefix, so that I can organize my multi-location parking operations.

## Acceptance Criteria

### Create Site
- **AC1**: Admin navigates to `/admin/settings/sites` → Clicks "新增停車場" → Modal opens with form fields
- **AC2**: Required fields: 停車場名稱* (name), 前綴* (prefix), 地址 (address), 月租基本價格* (monthly_base_price), 日租基本價格* (daily_base_price)
- **AC3**: Name validation: 2-50 characters, unique across all sites (error: "此停車場名稱已存在")
- **AC4**: Prefix validation: 1-5 uppercase characters or Chinese (e.g., "A", "B", "停A"), unique across all sites (error: "此前綴已被使用")
- **AC5**: Prefix is immutable after creation (spaces depend on it for naming)
- **AC6**: Address: Optional, max 200 characters
- **AC7**: Base prices: Required, integer ≥ 0, in NT$ whole dollars
- **AC8**: On save → Site created, toast: "停車場已建立", redirect to site list
- **AC9**: Action logged: action='CREATE_SITE', new_values={name, prefix, address, monthly_base_price, daily_base_price}

### View Site List
- **AC10**: Site list page displays table with columns: 名稱, 前綴, 地址, 月租基本價, 日租基本價, 車位數, 狀態, 操作
- **AC11**: Each site row shows: name, prefix, address (truncated), base prices (NT$ format), space count (total/occupied), status badge, edit/deactivate actions
- **AC12**: Status badges: 啟用中 (active, green) / 已停用 (inactive, gray)

### Edit Site
- **AC13**: Admin clicks "編輯" on a site → Modal opens pre-filled with current values
- **AC14**: Editable fields: name, address, monthly_base_price, daily_base_price (prefix NOT editable)
- **AC15**: Changing base price → Warning: "修改基本價格將影響使用站點預設價格的 X 個車位" with count of affected spaces (price_source='site_base')
- **AC16**: On save → Site updated, affected spaces using site_base price auto-updated, toast: "停車場已更新"
- **AC17**: Action logged: action='UPDATE_SITE', old_values={...}, new_values={...}

### Deactivate/Reactivate Site
- **AC18**: Admin clicks "停用" on active site → Confirmation: "確定要停用此停車場嗎？停用後此停車場的車位將不可新增合約。"
- **AC19**: Deactivation blocked if site has any active agreements (error: "此停車場尚有 X 份進行中合約，無法停用")
- **AC20**: Deactivated site: spaces hidden from agreement creation dropdown, existing agreements unaffected
- **AC21**: Admin can reactivate → "重新啟用" button, toast: "停車場已重新啟用"
- **AC22**: Action logged: action='UPDATE_SITE', old_values={is_active: true/false}, new_values={is_active: false/true}

## Business Rules

### Site Naming
- Site name must be unique (case-sensitive)
- Prefix must be unique, 1-5 characters (uppercase letters, digits, Chinese characters)
- Prefix cannot be changed after creation (spaces reference it for naming format)

### Site Deactivation
- Soft deactivation only (no deletion) — preserves historical data
- Cannot deactivate if active agreements exist on any space in the site
- Deactivated sites: spaces not available for new agreements, but visible in reports/history
- All spaces under a deactivated site inherit the restriction (no new agreements)

### Price Propagation
- Changing site base price auto-updates all spaces with `price_source='site_base'`
- Spaces with `price_source='custom'` or `price_source='tag'` are NOT affected
- Price propagation is immediate and logged

### Default Data
- System ships with 3 pre-configured sites (based on Wu family's actual parking lots)
- Admin can modify defaults and add new sites

## UI Requirements

### Site Settings Page
**Location**: `/admin/settings/sites`

**Page Structure**:
1. Page header: "停車場管理" + "新增停車場" button
2. Site table

**Table Columns**:
| 名稱 | 前綴 | 地址 | 月租基本價 | 日租基本價 | 車位數 | 狀態 | 操作 |
|------|------|------|-----------|-----------|--------|------|------|
| A區停車場 | A | 屏東市XX路100號 | NT$3,600 | NT$150 | 30/35 | 啟用中 | 編輯 \| 停用 |

### Create/Edit Site Modal
**Fields**:
- **停車場名稱 * (Site Name)**:
  - Type: Text input
  - Placeholder: "例如：A區停車場"
  - Validation: Required, 2-50 chars, unique

- **前綴 * (Prefix)** (create only, read-only on edit):
  - Type: Text input
  - Placeholder: "例如：A"
  - Validation: Required, 1-5 chars, uppercase/Chinese, unique
  - Help text: "前綴用於車位命名，例如前綴 A 的車位將命名為 A-01、A-02..."

- **地址 (Address)**:
  - Type: Text input
  - Placeholder: "例如：屏東市XX路100號"
  - Optional, max 200 chars

- **月租基本價格 * (Monthly Base Price)**:
  - Type: Number input with NT$ prefix
  - Validation: Required, integer ≥ 0

- **日租基本價格 * (Daily Base Price)**:
  - Type: Number input with NT$ prefix
  - Validation: Required, integer ≥ 0

**Actions**: "儲存" (primary) | "取消" (secondary)

## Implementation Notes

### Database Schema

```sql
CREATE TABLE sites (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE CHECK (char_length(name) >= 2 AND char_length(name) <= 50),
  prefix TEXT NOT NULL UNIQUE CHECK (char_length(prefix) >= 1 AND char_length(prefix) <= 5),
  address TEXT CHECK (char_length(address) <= 200),
  monthly_base_price INTEGER NOT NULL DEFAULT 3600 CHECK (monthly_base_price >= 0),
  daily_base_price INTEGER NOT NULL DEFAULT 150 CHECK (daily_base_price >= 0),
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_sites_is_active ON sites(is_active);
```

### Price Propagation on Update
```typescript
async function updateSiteBasePrice(siteId: string, newMonthly: number, newDaily: number) {
  // Update spaces using site_base pricing
  await db.spaces.updateMany(
    { site_id: siteId, price_source: 'site_base' },
    { monthly_price: newMonthly, daily_price: newDaily }
  );
}
```

## Source
init_draft.md (multi-location management), CLAUDE.md (site management)

## Dependencies
- US-SPACE-003 (pricing model — base prices defined here)
- US-AUDIT-002 (audit logging)
- US-LOC-003 (TWD currency format)

## Test Data

### Sites
**Site A**:
- Name: A區停車場
- Prefix: A
- Address: 屏東市中正路100號
- Monthly base: NT$3,600
- Daily base: NT$150
- Spaces: 35 total, 28 occupied
- Status: active

**Site B**:
- Name: B區停車場
- Prefix: B
- Address: 屏東市民生路50號
- Monthly base: NT$4,200
- Daily base: NT$180
- Spaces: 40 total, 35 occupied
- Status: active

**Site C**:
- Name: C區停車場
- Prefix: C
- Address: 屏東市復興路200號
- Monthly base: NT$3,000
- Daily base: NT$120
- Spaces: 25 total, 15 occupied
- Status: active

### Validation Errors
- Empty name: "停車場名稱為必填欄位"
- Duplicate name: "此停車場名稱已存在"
- Empty prefix: "前綴為必填欄位"
- Duplicate prefix: "此前綴已被使用"
- Negative price: "價格不可為負數"

### Deactivation Scenarios
**Cannot deactivate**: Site A has 28 active agreements → "此停車場尚有 28 份進行中合約，無法停用"
**Can deactivate**: Site C has 0 active agreements → Deactivation succeeds, spaces hidden from new agreements
