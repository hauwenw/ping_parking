# US-AGREE-009: Agreement List View (with Payment Status)

**Priority**: Must Have | **Phase**: Phase 1 | **Sprint**: Sprint 4 (Weeks 7-8)
**Domain**: Agreement Management | **Epic**: Agreement Views

## User Story
As a parking lot admin, I want to view a list of all agreements with payment status, filtering, and search capabilities, so that I can manage contracts, track revenue, identify late payments, and monitor overall operations from a single page.

## Acceptance Criteria

### Agreement List Display
- **AC1**: Agreement list page displays table with columns: 客戶, 車位, 類型, 合約期間, 金額, 付款狀態, 合約狀態, 操作
- **AC2**: Each row shows:
  - Customer: Name (clickable link to customer detail)
  - Space: Site-Space (e.g., "A區-01", clickable link to space detail)
  - Type: 日租/月租/季租/年租
  - Period: YYYY/MM/DD 至 YYYY/MM/DD
  - Amount: NT$X,XXX
  - Payment status: Badge (待付款 yellow / 已付款 green / 已作廢 gray / ⚠️逾期 red)
  - Agreement status: Badge (待生效 blue / 進行中 green / 已過期 gray / 已終止 dark gray)
  - Actions: "查看" link → Agreement detail, "記錄付款" (if payment pending)
- **AC3**: Overdue payments (current_date > due_date AND payment status='pending') show red "⚠️ 逾期 X 天" badge in payment status column
- **AC4**: Default sort: Start date descending (newest first)
- **AC5**: Pagination: 20 agreements per page

### Search & Filters
- **AC6**: Search bar: "搜尋客戶姓名、車位、車牌、銀行參考號碼" (partial match, case-insensitive)
- **AC7**: Agreement status filter: "全部狀態" / "待生效" / "進行中" / "已過期" / "已終止"
- **AC8**: Payment status filter: "全部付款狀態" / "待付款" / "已付款" / "已作廢" / "逾期未付"
- **AC9**: Agreement type filter: "全部類型" / "日租" / "月租" / "季租" / "年租"
- **AC10**: Site filter: "全部停車場" / site names
- **AC11**: Date range filter: "合約期間" (start date range picker)
- **AC12**: "清除篩選" button: Resets all filters to default
- **AC13**: Filter combination: All filters applied together via AND logic
- **AC14**: Result count: "顯示 1-20 筆，共 85 筆合約"

### Sorting
- **AC15**: Sortable columns: 合約期間 (start date), 金額 (amount), 合約狀態 (status)
- **AC16**: Sort indicator: ↑ (ascending) or ↓ (descending) next to column header
- **AC17**: Default: Start date descending (newest first)

### Quick Stats (Summary Cards)
- **AC18**: Top of page shows 4 summary cards:
  - 待付款總額: NT$XX,XXX (sum of pending payments) with count
  - 已付款總額 (本月): NT$XX,XXX (sum of completed payments this month) with count
  - 逾期付款: X 筆 (count of overdue pending payments) with total amount
  - 進行中合約: X 筆 (count of active agreements)

### Quick Actions
- **AC19**: "記錄付款" action on each row (only for pending payment status) → Opens record payment modal (per US-PAY-002)
- **AC20**: "新增合約" button at top of page → Opens agreement creation form

### Empty States
- **AC21**: No agreements exist → "目前沒有合約記錄" with "新增合約" button
- **AC22**: No search results → "找不到符合條件的合約" with "清除篩選" button

## Business Rules

### Agreement List Scope
- Shows all agreements across all sites
- Includes all statuses: pending, active, expired, terminated
- Agreement status computed from dates (per US-AGREE-006), not stored
- Payment status from linked payment record (1:1)

### Overdue Logic
- Payment is overdue if: `payment.status='pending' AND current_date > payment.due_date`
- Overdue badge shown in red: "⚠️ 逾期 X 天"
- Days overdue = `current_date - payment.due_date`

### Cross-Navigation
- Customer name → Customer detail page
- Space name → Space detail page
- "查看" action → Agreement detail page (includes full payment section)
- All links open in same tab

### Performance
- Server-side pagination and filtering
- Computed status calculated in query (no stored status for pending/active/expired)

## UI Requirements

### Page Layout
**Location**: `/admin/agreements`
**Navigation**: Top nav "合約管理" link

**Page Structure**:
1. Page header: "合約管理" + "新增合約" button
2. Summary cards row (4 cards)
3. Search & filter bar
4. Agreement table
5. Pagination controls

### Summary Cards
**Layout**: 4-column grid (responsive to 2x2 on tablet)

**Card 1 - 待付款總額**:
- Amount: NT$45,600
- Label: "待付款總額"
- Count: "15 筆"

**Card 2 - 已付款總額 (本月)**:
- Amount: NT$128,000
- Label: "已付款總額 (本月)"
- Count: "32 筆"

**Card 3 - 逾期付款**:
- Count: 5 (large, red)
- Label: "逾期付款"
- Subtext: "總額 NT$18,000"

**Card 4 - 進行中合約**:
- Count: 68
- Label: "進行中合約"

### Search & Filter Bar
**Layout**: Single row with controls

**Search Input**:
- Width: 300px
- Placeholder: "搜尋客戶姓名、車位、車牌、銀行參考號碼"
- Icon: Magnifying glass (left)

**Filter Dropdowns**:
- 合約狀態: "全部狀態" ▼
- 付款狀態: "全部付款狀態" ▼
- 類型: "全部類型" ▼
- 停車場: "全部停車場" ▼
- 合約期間: Date range picker

**Clear Button**: "清除篩選" (visible when any filter applied)

### Agreement Table
**Columns**:
| 客戶 | 車位 | 類型 | 合約期間 ↓ | 金額 | 付款狀態 | 合約狀態 | 操作 |
|------|------|------|-----------|------|---------|---------|------|
| 王小明 | A-01 | 月租 | 02/01-03/01 | NT$4,000 | 已付款 ✓ | 進行中 | 查看 |
| 李小華 | B-05 | 月租 | 01/25-02/25 | NT$3,600 | ⚠️逾期21天 | 進行中 | 查看 \| 記錄付款 |
| 張小美 | C-02 | 月租 | 02/01-03/01 | ~~NT$3,800~~ | 已作廢 | 已終止 | 查看 |

**Payment Status Badges**:
- 待付款: Yellow badge
- 已付款: Green badge with ✓
- 已作廢: Gray badge with strikethrough amount
- ⚠️逾期 X 天: Red badge (next to 待付款)

**Agreement Status Badges**:
- 待生效: Blue badge
- 進行中: Green badge
- 已過期: Gray badge
- 已終止: Dark gray badge

**Row Hover**: Highlight entire row, cursor pointer

### Pagination
**Position**: Bottom-right of table
**Format**: "顯示 1-20 筆，共 85 筆合約"
**Controls**: "上一頁" | 1 2 3 ... 5 | "下一頁"

## Implementation Notes

### SQL Query with Filters
```sql
SELECT
  a.*,
  c.name AS customer_name,
  s.name AS space_name,
  sites.name AS site_name,
  a.license_plates,
  p.amount AS payment_amount,
  p.status AS payment_status,
  p.due_date AS payment_due_date,
  p.payment_date,
  p.bank_ref,
  CASE
    WHEN a.status = 'terminated' THEN 'terminated'
    WHEN CURRENT_DATE < a.start_date THEN 'pending'
    WHEN CURRENT_DATE <= a.end_date THEN 'active'
    ELSE 'expired'
  END AS computed_status,
  CASE
    WHEN p.status = 'pending' AND CURRENT_DATE > p.due_date
    THEN CURRENT_DATE - p.due_date
    ELSE 0
  END AS days_overdue
FROM agreements a
JOIN customers c ON a.customer_id = c.id
JOIN spaces s ON a.space_id = s.id
JOIN sites ON s.site_id = sites.id
LEFT JOIN payments p ON p.agreement_id = a.id
WHERE 1=1
  AND (:search IS NULL
    OR c.name ILIKE '%' || :search || '%'
    OR s.name ILIKE '%' || :search || '%'
    OR array_to_string(a.license_plates, ',') ILIKE '%' || :search || '%'
    OR p.bank_ref ILIKE '%' || :search || '%'
  )
  AND (:agreement_status IS NULL
    OR (:agreement_status = 'terminated' AND a.status = 'terminated')
    OR (:agreement_status = 'pending' AND a.status != 'terminated' AND CURRENT_DATE < a.start_date)
    OR (:agreement_status = 'active' AND a.status != 'terminated' AND CURRENT_DATE BETWEEN a.start_date AND a.end_date)
    OR (:agreement_status = 'expired' AND a.status != 'terminated' AND CURRENT_DATE > a.end_date)
  )
  AND (:payment_status IS NULL
    OR p.status = :payment_status
    OR (:payment_status = 'overdue' AND p.status = 'pending' AND CURRENT_DATE > p.due_date)
  )
  AND (:agreement_type IS NULL OR a.agreement_type = :agreement_type)
  AND (:site_id IS NULL OR s.site_id = :site_id)
  AND (:start_from IS NULL OR a.start_date >= :start_from)
  AND (:start_to IS NULL OR a.start_date <= :start_to)
ORDER BY a.start_date DESC
LIMIT 20 OFFSET :offset;
```

### Summary Stats Query
```sql
-- Pending payment total
SELECT COUNT(*), SUM(p.amount) FROM payments p WHERE p.status = 'pending';

-- Completed this month
SELECT COUNT(*), SUM(p.amount) FROM payments p
WHERE p.status = 'completed'
AND DATE_TRUNC('month', p.payment_date) = DATE_TRUNC('month', CURRENT_DATE);

-- Overdue count and total
SELECT COUNT(*), SUM(p.amount) FROM payments p
WHERE p.status = 'pending' AND CURRENT_DATE > p.due_date;

-- Active agreements
SELECT COUNT(*) FROM agreements a
WHERE a.status != 'terminated'
AND CURRENT_DATE BETWEEN a.start_date AND a.end_date;
```

## Source
Consolidation of US-PAY-003 (payment list) into agreement domain. Payment is 1:1 with agreement.

## Dependencies
- US-AGREE-001 (agreement creation)
- US-AGREE-006 (computed status)
- US-PAY-001 (payment lifecycle)
- US-PAY-002 (record payment — modal reused from agreement list)
- US-SPACE-005 (space list for cross-nav)
- US-CUST-002 (customer detail for cross-nav)
- US-LOC-003 (TWD currency format)
- US-LOC-004 (Taiwan date format)

## Test Data

### Agreement List (Mixed Statuses)
**Agreement 1** (active, paid):
- Customer: 王小明, Space: A-01, Type: 月租
- Period: 2026-02-01 至 2026-03-01
- Amount: NT$4,000, Payment: completed, Bank ref: TXN-20260205-001
- Agreement status: 進行中, Payment status: 已付款

**Agreement 2** (active, overdue):
- Customer: 李小華, Space: B-05, Type: 月租
- Period: 2026-01-25 至 2026-02-25
- Amount: NT$3,600, Payment: pending, Due: 2026-01-25
- Agreement status: 進行中, Payment status: ⚠️逾期21天

**Agreement 3** (terminated, voided):
- Customer: 張小美, Space: C-02, Type: 月租
- Period: 2026-02-01 至 2026-03-01
- Amount: NT$3,800, Payment: voided
- Agreement status: 已終止, Payment status: 已作廢

**Agreement 4** (pending, pending payment):
- Customer: 陳大同, Space: A-05, Type: 季租
- Period: 2026-03-01 至 2026-06-01
- Amount: NT$12,600, Payment: pending, Due: 2026-03-01
- Agreement status: 待生效, Payment status: 待付款

### Summary Stats (Sample)
- 待付款總額: NT$45,600 (15筆)
- 已付款總額 (本月): NT$128,000 (32筆)
- 逾期付款: 5筆 (總額 NT$18,000)
- 進行中合約: 68筆
