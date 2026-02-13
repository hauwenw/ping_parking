# US-SPACE-005: Space List View (Table with Filters)

**Priority**: Must Have | **Phase**: Phase 1 | **Sprint**: Sprint 2 (Weeks 3-4)
**Domain**: Space Management | **Epic**: Space Views

## User Story
As a parking lot admin, I want to view all parking spaces in a filterable, sortable table with availability and pricing information, so that I can quickly find and manage spaces across all sites.

## Acceptance Criteria

### Space Table Display
- **AC1**: Space list page displays table with columns: 車位, 停車場, 標籤, 月租價格, 日租價格, 狀態, 目前租客, 操作
- **AC2**: Each row shows:
  - Space name: e.g., "A-01"
  - Site: Site name (e.g., "A區停車場")
  - Tags: Color dots with tag names (e.g., [blue dot] 有屋頂, [green dot] 大車位)
  - Monthly price: NT$X,XXX
  - Daily price: NT$XXX
  - Status: Badge (可租用 green / 已租出 red / 維護中 orange / 已預留 blue)
  - Current tenant: Customer name + license plate (if occupied), or "—" if available
  - Actions: "查看" link → Space detail page
- **AC3**: Default sort: Space name ascending (A-01, A-02, ..., B-01, ...)
- **AC4**: Pagination: 20 spaces per page

### Space Status (Computed + Manual)
- **AC5**: Status is determined by combining computed availability and manual status:
  - **可租用 (available, green)**: No active agreement covers current_date AND manual_status IS NULL
  - **已租出 (occupied, red)**: Non-terminated agreement exists where start_date ≤ current_date ≤ end_date
  - **維護中 (maintenance, orange)**: manual_status = 'maintenance' (overrides computed status)
  - **已預留 (reserved, blue)**: manual_status = 'reserved' (overrides computed status)
- **AC6**: Manual status (maintenance/reserved) takes precedence — space shows as maintenance/reserved even if an agreement covers it
- **AC7**: Spaces in maintenance/reserved status are excluded from agreement creation dropdown

### Search & Filters
- **AC8**: Search bar: "搜尋車位名稱" (partial match, e.g., "A-0" matches A-01 through A-09)
- **AC9**: Site filter dropdown: "全部停車場" / site names (shows active sites only)
- **AC10**: Status filter dropdown: "全部狀態" / "可租用" / "已租出" / "維護中" / "已預留"
- **AC11**: Tag filter: Multi-select dropdown "全部標籤" / tag names with color dots
  - Tag filter uses AND logic: selecting "有屋頂" + "VIP" shows spaces with BOTH tags
- **AC12**: "清除篩選" button: Resets all filters to default
- **AC13**: Filter combination: Search + Site + Status + Tags (all applied together via AND logic)
- **AC14**: Result count: "顯示 1-20 筆，共 100 個車位"

### Sorting
- **AC15**: Sortable columns: 車位 (name), 月租價格 (monthly price), 狀態 (status)
- **AC16**: Sort indicator: ↑ (ascending) or ↓ (descending) next to column header
- **AC17**: Default: Space name ascending

### Empty States
- **AC18**: No spaces exist → "目前沒有車位資料" with "新增車位" and "批量新增" buttons
- **AC19**: No search results → "找不到符合條件的車位" with "清除篩選" button

### Quick Stats (Summary Row)
- **AC20**: Above table, show summary: "共 100 個車位：可租用 25 | 已租出 68 | 維護中 3 | 已預留 4"

## Business Rules

### Status Computation
- **Computed availability**: Derived from agreements table — "occupied" if non-terminated agreement covers current_date
- **Manual status**: Admin-set override — 'maintenance' or 'reserved'
- **Priority**: Manual status > Computed availability
- **Maintenance/reserved spaces**: Cannot create new agreements (excluded from space selection dropdown in agreement form)

### Agreement Form Integration
- Agreement creation space dropdown shows ALL spaces with availability indicator:
  - "A-01 (可租用)" — selectable
  - "A-02 (已租出 至 2026-03-01)" — selectable (for future-dated agreements)
  - "A-03 (維護中)" — disabled, not selectable
  - "A-04 (已預留)" — disabled, not selectable

### Tag Filtering
- Uses PostgreSQL `@>` operator for array containment
- AND logic: multiple tag filters = spaces must have ALL selected tags
- Tags displayed as colored dots with names for quick visual scanning

### Performance
- Server-side pagination and filtering (not client-side)
- Indexed queries on site_id, tags (GIN), and agreement status

## UI Requirements

### Page Layout
**Location**: `/admin/spaces`
**Navigation**: Top nav "停車場管理" → "車位管理" tab

**Page Structure**:
1. Page header: "車位管理" + "新增車位" + "批量新增" buttons
2. Quick stats summary
3. Search & filter bar
4. Space table
5. Pagination controls

### Quick Stats
**Format**: Single line above filters
```
共 100 個車位：可租用 25 | 已租出 68 | 維護中 3 | 已預留 4
```
- Each status count uses its respective badge color

### Search & Filter Bar
**Layout**: Single row with controls

**Search Input**:
- Width: 250px
- Placeholder: "搜尋車位名稱"
- Icon: Magnifying glass (left)

**Filter Dropdowns**:
- 停車場: "全部停車場" ▼ (single-select)
- 狀態: "全部狀態" ▼ (single-select)
- 標籤: "全部標籤" ▼ (multi-select with checkboxes, color dots)

**Clear Button**: "清除篩選" (visible when any filter applied)

### Space Table
**Columns**:
| 車位 ↑ | 停車場 | 標籤 | 月租價格 | 日租價格 | 狀態 | 目前租客 | 操作 |
|--------|--------|------|---------|---------|------|---------|------|
| A-01 | A區停車場 | [blue]有屋頂 | NT$4,000 | NT$180 | 已租出 | 王小明 (ABC-1234) | 查看 |
| A-02 | A區停車場 | [green]大車位 | NT$3,600 | NT$150 | 可租用 | — | 查看 |
| A-03 | A區停車場 | | NT$3,600 | NT$150 | 維護中 | — | 查看 |

**Status Badges**:
- 可租用: Green badge
- 已租出: Red badge
- 維護中: Orange badge
- 已預留: Blue badge

**Row Hover**: Highlight entire row, cursor pointer (click → space detail)

**Actions Column**: "查看" link

### Pagination
**Position**: Bottom-right of table
**Format**: "顯示 1-20 筆，共 100 個車位"
**Controls**: "上一頁" | 1 2 3 ... 5 | "下一頁"

## Implementation Notes

### SQL Query with Filters
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
  END AS computed_status,
  -- Current tenant info (if occupied)
  (
    SELECT json_build_object('name', c.name, 'license_plates', a.license_plates)
    FROM agreements a
    JOIN customers c ON a.customer_id = c.id
    WHERE a.space_id = s.id
    AND a.status != 'terminated'
    AND CURRENT_DATE BETWEEN a.start_date AND a.end_date
    LIMIT 1
  ) AS current_tenant
FROM spaces s
JOIN sites ON s.site_id = sites.id
WHERE 1=1
  AND (:search IS NULL OR s.name ILIKE '%' || :search || '%')
  AND (:site_id IS NULL OR s.site_id = :site_id)
  AND (:tags IS NULL OR s.tags @> :tags)
  -- Status filter applied in HAVING or subquery
ORDER BY s.name ASC
LIMIT 20 OFFSET :offset;
```

### Summary Stats Query
```sql
SELECT
  COUNT(*) AS total,
  COUNT(*) FILTER (WHERE computed_status = 'available') AS available,
  COUNT(*) FILTER (WHERE computed_status = 'occupied') AS occupied,
  COUNT(*) FILTER (WHERE computed_status = 'maintenance') AS maintenance,
  COUNT(*) FILTER (WHERE computed_status = 'reserved') AS reserved
FROM (
  SELECT s.*,
    CASE
      WHEN s.manual_status = 'maintenance' THEN 'maintenance'
      WHEN s.manual_status = 'reserved' THEN 'reserved'
      WHEN EXISTS (...) THEN 'occupied'
      ELSE 'available'
    END AS computed_status
  FROM spaces s
) sub;
```

## Source
init_draft.md line 92 (space grid), CLAUDE.md (space management)

## Dependencies
- US-SPACE-001 (sites for filter dropdown)
- US-SPACE-002 (spaces data)
- US-SPACE-004 (tags for filter dropdown)
- US-AGREE-006 (agreement status for occupancy computation)
- US-LOC-003 (TWD currency format)

## Test Data

### Space List (Mixed Statuses)
**A-01** (occupied):
- Site: A區停車場
- Tags: [有屋頂]
- Monthly: NT$4,000, Daily: NT$180
- Status: 已租出
- Tenant: 王小明 (ABC-1234)

**A-02** (available):
- Site: A區停車場
- Tags: [大車位]
- Monthly: NT$3,600, Daily: NT$150
- Status: 可租用
- Tenant: —

**A-03** (maintenance):
- Site: A區停車場
- Tags: []
- Monthly: NT$3,600, Daily: NT$150
- Status: 維護中
- Tenant: —

**B-01** (reserved):
- Site: B區停車場
- Tags: [VIP, 有屋頂]
- Monthly: NT$5,000, Daily: NT$220
- Status: 已預留
- Tenant: —

### Filter Examples
**Site filter: "B區停車場"** → Only B-site spaces
**Status filter: "可租用"** → Available spaces only
**Tag filter: ["有屋頂"]** → Spaces with 有屋頂 tag
**Combined: Site A + Status 可租用 + Tag 大車位** → Available A-site spaces with 大車位 tag

### Summary Stats
共 100 個車位：可租用 25 | 已租出 68 | 維護中 3 | 已預留 4
