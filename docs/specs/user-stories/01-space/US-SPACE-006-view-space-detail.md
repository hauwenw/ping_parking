# US-SPACE-006: View Space Detail

**Priority**: Must Have | **Phase**: Phase 1 | **Sprint**: Sprint 2 (Weeks 3-4)
**Domain**: Space Management | **Epic**: Space Views

## User Story
As a parking lot admin, I want to view detailed information about a parking space including its pricing, tags, current status, agreement history, and manual status controls, so that I can manage individual spaces effectively.

## Acceptance Criteria

### Space Information Card
- **AC1**: Space detail page shows: 車位名稱, 停車場, 標籤 (with color dots), 月租價格, 日租價格, 價格來源, 狀態, 備註
- **AC2**: Price source displayed as: "站點預設" / "自訂價格" / "標籤: {tag_name}"
- **AC3**: Status badge: 可租用 (green) / 已租出 (red) / 維護中 (orange) / 已預留 (blue)

### Manual Status Control
- **AC4**: Admin can set manual status via dropdown: "正常" (clears manual_status) / "維護中" / "已預留"
- **AC5**: Setting to "維護中" → Confirmation: "設為維護中後，此車位將無法新增合約。是否繼續？"
- **AC6**: Setting to "已預留" → Optional reason input (stored in notes): "預留原因（選填）"
- **AC7**: If space has active agreement AND admin sets to maintenance → Warning: "此車位目前有進行中合約 (至 YYYY-MM-DD)，設為維護中不影響現有合約，但到期後將無法續約。"
- **AC8**: Clearing manual status (back to "正常") → Toast: "車位狀態已恢復正常"
- **AC9**: All manual status changes logged to system_logs

### Current Agreement Section
- **AC10**: If space is occupied → Shows current agreement info:
  - Customer name (link to customer detail)
  - License plates
  - Agreement type (日租/月租/季租/年租)
  - Agreement period: YYYY年MM月DD日 至 YYYY年MM月DD日
  - Payment status: 待付款 / 已付款 / 已作廢
  - "查看合約" link → Agreement detail page
- **AC11**: If space is available → Shows "目前無租用合約" message

### Agreement History
- **AC12**: Table showing all agreements (past and present) for this space:
  - Columns: 客戶, 類型, 合約期間, 金額, 狀態
  - Sorted by start_date descending (newest first)
  - Status badges: 待生效 (blue) / 進行中 (green) / 已過期 (gray) / 已終止 (dark gray)
- **AC13**: Each row clickable → navigates to agreement detail
- **AC14**: Empty state: "此車位尚無合約記錄"

### Action Buttons
- **AC15**: "編輯車位" → Opens edit modal (US-SPACE-002)
- **AC16**: "刪除車位" → Deletion flow (US-SPACE-002, blocked if active agreements)
- **AC17**: "新增合約" → Opens agreement creation form pre-filled with this space (only if available and not maintenance/reserved)

## Business Rules

### Status Determination
Priority order:
1. `manual_status = 'maintenance'` → 維護中 (orange)
2. `manual_status = 'reserved'` → 已預留 (blue)
3. Active agreement covers current_date → 已租出 (red)
4. No active agreement → 可租用 (green)

### Manual Status Effects
- **Maintenance**: Space excluded from agreement creation, existing agreements unaffected, cannot renew after expiry
- **Reserved**: Same restrictions as maintenance — space held for a specific purpose
- Both statuses can be set/cleared at any time by admin
- Manual status persists until explicitly cleared

### Agreement History Scope
- Shows ALL agreements for this space, regardless of status
- Includes: active, pending, expired, terminated
- Provides full occupancy history for the space

### Cross-Navigation
- Customer name → Customer detail page (`/admin/customers/:id`)
- Agreement row → Agreement detail page (`/admin/agreements/:id`)
- All links open in same tab

## UI Requirements

### Page Layout
**Location**: `/admin/spaces/:spaceId`

**Page Structure**:
1. Page header: Space name + Status badge + Action buttons
2. Space information card
3. Manual status control
4. Current agreement section (if occupied)
5. Agreement history table

### Page Header
```
A-01 [已租出]                    [編輯車位] [刪除車位] [新增合約]
A區停車場
```
- Space name: Large, bold
- Status badge: Next to name
- Site name: Subtitle, gray text
- Action buttons: Top-right

### Space Information Card
**Layout**: 2-column grid

| Field | Value |
|-------|-------|
| 車位名稱 | A-01 |
| 停車場 | A區停車場 |
| 標籤 | [blue dot] 有屋頂 [green dot] 大車位 |
| 月租價格 | NT$4,000 (標籤: 有屋頂) |
| 日租價格 | NT$180 (標籤: 有屋頂) |
| 狀態 | 已租出 |
| 備註 | — |

### Manual Status Control
**Section**: Card with title "車位狀態設定"

**Dropdown**: Current status displayed as selected option
- "正常 (自動判定)" → Clears manual_status
- "維護中" → Sets manual_status='maintenance'
- "已預留" → Sets manual_status='reserved'

**Save Button**: "更新狀態"

### Current Agreement Section
**Section**: Card with title "目前租用合約"

**If occupied**:
```
客戶：王小明                    [查看合約]
車牌：ABC-1234, XYZ-9999
類型：月租
期間：2026年02月01日 至 2026年03月01日
付款：已付款 (NT$4,000)
```

**If available**: "目前無租用合約" + "新增合約" button

### Agreement History Table
**Section**: Card with title "合約歷史"

| 客戶 | 類型 | 合約期間 | 金額 | 狀態 |
|------|------|---------|------|------|
| 王小明 | 月租 | 2026-02-01 至 2026-03-01 | NT$4,000 | 進行中 |
| 李小華 | 月租 | 2026-01-01 至 2026-02-01 | NT$3,600 | 已過期 |
| 張小美 | 季租 | 2025-10-01 至 2026-01-01 | NT$10,800 | 已過期 |

## Implementation Notes

### Space Detail Query
```sql
SELECT
  s.*,
  sites.name AS site_name,
  sites.prefix AS site_prefix,
  CASE
    WHEN s.manual_status = 'maintenance' THEN 'maintenance'
    WHEN s.manual_status = 'reserved' THEN 'reserved'
    WHEN EXISTS (
      SELECT 1 FROM agreements a
      WHERE a.space_id = s.id
      AND a.status != 'terminated'
      AND CURRENT_DATE BETWEEN a.start_date AND a.end_date
    ) THEN 'occupied'
    ELSE 'available'
  END AS computed_status
FROM spaces s
JOIN sites ON s.site_id = sites.id
WHERE s.id = :spaceId;
```

### Current Agreement Query
```sql
SELECT a.*, c.name AS customer_name, p.status AS payment_status, p.amount AS payment_amount
FROM agreements a
JOIN customers c ON a.customer_id = c.id
LEFT JOIN payments p ON p.agreement_id = a.id
WHERE a.space_id = :spaceId
AND a.status != 'terminated'
AND CURRENT_DATE BETWEEN a.start_date AND a.end_date
LIMIT 1;
```

### Agreement History Query
```sql
SELECT
  a.*,
  c.name AS customer_name,
  CASE
    WHEN a.status = 'terminated' THEN 'terminated'
    WHEN CURRENT_DATE < a.start_date THEN 'pending'
    WHEN CURRENT_DATE <= a.end_date THEN 'active'
    ELSE 'expired'
  END AS computed_status
FROM agreements a
JOIN customers c ON a.customer_id = c.id
WHERE a.space_id = :spaceId
ORDER BY a.start_date DESC;
```

### Manual Status Update
```typescript
async function updateManualStatus(
  spaceId: string,
  manualStatus: 'maintenance' | 'reserved' | null,
  reason?: string
) {
  const space = await getSpace(spaceId);
  const oldStatus = space.manual_status;

  await db.spaces.update(spaceId, {
    manual_status: manualStatus,
    notes: reason || space.notes,
    updated_at: new Date()
  });

  await logToAudit('UPDATE_SPACE', {
    space_id: spaceId,
    old_values: { manual_status: oldStatus },
    new_values: { manual_status: manualStatus, reason }
  });
}
```

## Source
init_draft.md (space detail), CLAUDE.md (space status)

## Dependencies
- US-SPACE-001 (site info display)
- US-SPACE-002 (edit/delete actions)
- US-SPACE-003 (pricing display)
- US-SPACE-005 (navigated from space list)
- US-AGREE-005 (agreement detail navigation)
- US-AGREE-006 (agreement status computation)
- US-CUST-002 (customer detail navigation)
- US-AUDIT-002 (audit logging)

## Test Data

### Space Detail - Occupied
**Space A-01**:
- Site: A區停車場
- Tags: [有屋頂, 大車位]
- Monthly: NT$4,000, Daily: NT$180 (source: 標籤: 有屋頂)
- Manual status: NULL
- Computed status: 已租出
- Current agreement:
  - Customer: 王小明
  - License plates: ABC-1234, XYZ-9999
  - Type: 月租
  - Period: 2026-02-01 至 2026-03-01
  - Payment: 已付款 (NT$4,000)

### Space Detail - Available
**Space A-02**:
- Site: A區停車場
- Tags: [大車位]
- Monthly: NT$3,600, Daily: NT$150 (source: 站點預設)
- Manual status: NULL
- Computed status: 可租用
- Current agreement: None
- Agreement history: 3 past agreements (all expired)

### Space Detail - Maintenance
**Space A-03**:
- Manual status: maintenance
- Computed status: 維護中
- Has active agreement (edge case): Warning shown to admin
- Agreement history: visible but no new agreement allowed

### Manual Status Change Scenarios
**Set to maintenance**: A-02 (available) → admin sets 維護中 → "設為維護中後，此車位將無法新增合約。是否繼續？" → Confirm → Status changes
**Set to reserved with reason**: A-04 → admin sets 已預留, reason="等待VIP客戶" → Status changes, reason stored
**Clear manual status**: A-03 (maintenance) → admin selects "正常" → "車位狀態已恢復正常" → Status becomes 可租用 or 已租出 (computed)
