# US-PAY-003: View Payment History/List

**Priority**: Must Have | **Phase**: Phase 1 | **Sprint**: Sprint 4 (Weeks 7-8)
**Domain**: Payment Management | **Epic**: Payment Tracking

## User Story
As a parking lot admin, I want to view a list of all payments with filtering and search capabilities, so that I can track revenue, identify late payments, and manage customer payment status.

## Acceptance Criteria

### Payment List Display
- **AC1**: Payment list page displays table with columns: 付款日期, 到期日期, 客戶, 車位, 合約類型, 金額, 狀態, 操作
- **AC2**: Each row shows:
  - Payment date: YYYY年MM月DD日 (or "待付款" if pending)
  - Due date: YYYY年MM月DD日 (with overdue indicator if current_date > due_date AND status=pending)
  - Customer: Name (clickable link to customer detail)
  - Space: Site-Space (e.g., "A區-01", clickable link to agreement detail)
  - Agreement type: 日租/月租/季租/年租
  - Amount: NT$X,XXX
  - Status: Badge (待付款 yellow / 已付款 green / 已作廢 gray)
  - Actions: "查看" link → Payment detail page
- **AC3**: Overdue payments (current_date > due_date AND status='pending') show red "逾期" badge next to due date
- **AC4**: Default sort: Due date descending (newest first)
- **AC5**: Pagination: 20 payments per page

### Search & Filters
- **AC6**: Search bar: "搜尋客戶姓名、車位、銀行參考號碼" (partial match, case-insensitive)
- **AC7**: Status filter dropdown: "全部狀態" / "待付款" / "已付款" / "已作廢" / "逾期未付"
- **AC8**: Date range filter: "到期日期範圍" (start date + end date pickers)
- **AC9**: Amount range filter: "金額範圍" (min + max inputs)
- **AC10**: "清除篩選" button: Resets all filters to default
- **AC11**: Filter combination: Search + Status + Date range + Amount (all applied together via AND logic)
- **AC12**: Result count: "顯示 1-20 筆，共 156 筆付款"

### Sorting
- **AC13**: Sortable columns: 付款日期, 到期日期, 金額 (click column header to toggle asc/desc)
- **AC14**: Sort indicator: ↑ (ascending) or ↓ (descending) next to column name
- **AC15**: Default: Due date descending (newest first)

### Empty States
- **AC16**: No payments exist → "目前沒有付款記錄" with "新增合約" button (payments auto-generated from agreements)
- **AC17**: No search results → "找不到符合條件的付款記錄" with "清除篩選" button

### Quick Stats (Summary Cards)
- **AC18**: Top of page shows 4 summary cards:
  - 待付款總額: NT$XX,XXX (sum of pending payments)
  - 已付款總額: NT$XX,XXX (sum of completed payments this month)
  - 逾期付款: X 筆 (count of overdue pending payments)
  - 本月收款: NT$XX,XXX (sum of payments completed this month)

## Business Rules

### Payment List Scope
- Shows all payments across all agreements
- Includes pending, completed, and voided payments
- Real-time data (no caching for payment status)

### Overdue Logic
- Payment is overdue if: `status='pending' AND current_date > due_date`
- Overdue badge shown in red with warning icon: "⚠️ 逾期 X 天"
- Days overdue = `current_date - due_date`

### Cross-Navigation
- Customer name → Customer detail page
- Space name → Agreement detail page (not space detail)
- "查看" action → Payment detail page
- All links open in same tab

### Performance
- Pagination required (not infinite scroll)
- Filters applied server-side (not client-side)
- Total count cached for 1 minute (acceptable latency for count)

### Access Control
- Admin-only page (requires authentication per US-SEC-001)
- No public access to payment information

## UI Requirements

### Page Layout
**Location**: `/admin/payments`
**Navigation**: Top nav "付款管理" link

**Page Structure**:
1. Page header: "付款管理" + "匯出" button (future)
2. Summary cards row (4 cards)
3. Search & filter bar
4. Payment table
5. Pagination controls

### Summary Cards
**Layout**: 4-column grid (responsive to 2x2 on tablet)

**Card 1 - 待付款總額**:
- Icon: 💰 (yellow)
- Amount: NT$45,600
- Label: "待付款總額"
- Count: "15 筆"

**Card 2 - 已付款總額**:
- Icon: ✅ (green)
- Amount: NT$128,000
- Label: "已付款總額 (本月)"
- Count: "32 筆"

**Card 3 - 逾期付款**:
- Icon: ⚠️ (red)
- Count: 5 (large, red)
- Label: "逾期付款"
- Subtext: "總額 NT$18,000"

**Card 4 - 本月收款**:
- Icon: 📊 (blue)
- Amount: NT$95,000
- Label: "本月收款"
- Count: "24 筆"

### Search & Filter Bar
**Layout**: Single row with controls

**Search Input**:
- Width: 300px
- Placeholder: "搜尋客戶姓名、車位、銀行參考號碼"
- Icon: Magnifying glass (left)
- Clear button (× right) when text entered

**Filter Dropdowns**:
- Status: "全部狀態" ▼
- Date range: "到期日期範圍" ▼ → Opens date range picker
- Amount range: "金額範圍" ▼ → Opens min/max inputs

**Clear Button**: "清除篩選" (visible when any filter applied)

### Payment Table
**Columns**:
| 付款日期 | 到期日期 ↓ | 客戶 | 車位 | 類型 | 金額 | 狀態 | 操作 |
|---------|-----------|------|------|------|------|------|------|
| 2026-02-15 | 2026-02-01 | 王小明 | A-01 | 月租 | NT$4,000 | 已付款 | 查看 |
| 待付款 | 2026-01-25 ⚠️逾期21天 | 李小華 | B-05 | 月租 | NT$3,600 | 待付款 | 查看 |

**Status Badges**:
- 待付款: Yellow badge
- 已付款: Green badge with ✓
- 已作廢: Gray badge with strikethrough amount
- 逾期: Red "⚠️ 逾期 X 天" badge next to due date

**Row Hover**: Highlight entire row on hover, cursor pointer

**Actions Column**: "查看" link (blue, underlined on hover)

### Date Range Picker Modal
**Trigger**: Click "到期日期範圍" filter

**Fields**:
- 開始日期: Date picker (optional)
- 結束日期: Date picker (optional)
- Quick options: "本月" / "上月" / "本季" / "今年"

**Actions**: "套用" (primary) | "清除" (secondary)

### Amount Range Filter Modal
**Trigger**: Click "金額範圍" filter

**Fields**:
- 最低金額: NT$ input (optional, min=0)
- 最高金額: NT$ input (optional, min=0)

**Validation**: 最低金額 ≤ 最高金額 (error: "最低金額不可大於最高金額")

**Actions**: "套用" (primary) | "清除" (secondary)

### Pagination
**Position**: Bottom-right of table
**Format**: "顯示 1-20 筆，共 156 筆付款"
**Controls**: "上一頁" | 1 2 3 ... 8 | "下一頁"
**Behavior**: Disabled states on first/last page

## Implementation Notes

### SQL Query with Filters
```sql
-- Base query with joins
SELECT
  p.*,
  a.agreement_type,
  a.start_date AS agreement_start,
  c.name AS customer_name,
  s.name AS space_name,
  sites.name AS site_name,
  CASE
    WHEN p.status = 'pending' AND CURRENT_DATE > p.due_date
    THEN CURRENT_DATE - p.due_date
    ELSE 0
  END AS days_overdue
FROM payments p
JOIN agreements a ON p.agreement_id = a.id
JOIN customers c ON a.customer_id = c.id
JOIN spaces s ON a.space_id = s.id
JOIN sites ON s.site_id = sites.id
WHERE 1=1
  -- Search filter
  AND (
    :search IS NULL
    OR c.name ILIKE '%' || :search || '%'
    OR s.name ILIKE '%' || :search || '%'
    OR p.bank_ref ILIKE '%' || :search || '%'
  )
  -- Status filter
  AND (
    :status IS NULL
    OR p.status = :status
    OR (:status = 'overdue' AND p.status = 'pending' AND CURRENT_DATE > p.due_date)
  )
  -- Date range filter
  AND (:start_date IS NULL OR p.due_date >= :start_date)
  AND (:end_date IS NULL OR p.due_date <= :end_date)
  -- Amount range filter
  AND (:min_amount IS NULL OR p.amount >= :min_amount)
  AND (:max_amount IS NULL OR p.amount <= :max_amount)
ORDER BY p.due_date DESC
LIMIT 20 OFFSET :offset;
```

### Summary Stats Query
```sql
-- Pending total
SELECT SUM(amount) FROM payments WHERE status = 'pending';

-- Completed total (this month)
SELECT SUM(amount) FROM payments
WHERE status = 'completed'
AND DATE_TRUNC('month', payment_date) = DATE_TRUNC('month', CURRENT_DATE);

-- Overdue count and total
SELECT COUNT(*), SUM(amount) FROM payments
WHERE status = 'pending' AND CURRENT_DATE > due_date;

-- This month collected (by payment date)
SELECT SUM(amount), COUNT(*) FROM payments
WHERE status = 'completed'
AND DATE_TRUNC('month', payment_date) = DATE_TRUNC('month', CURRENT_DATE);
```

## Source
init_draft.md line 28 (payment tracking), 09-ui-ux/README.md (payment management page)

## Dependencies
- US-PAY-001 (payment lifecycle - defines payment structure)
- US-PAY-002 (record payment - completion action)
- US-AGREE-001 (agreements generate payments)
- US-CUST-002 (customer detail for navigation)
- US-LOC-003 (TWD currency format)
- US-LOC-004 (Taiwan date format)

## Test Data

### Payment List (Mixed Statuses)
**Payment 1**:
- Due date: 2026-02-01
- Payment date: 2026-02-05
- Customer: 王小明
- Space: A區-01
- Type: 月租
- Amount: NT$4,000
- Status: completed
- Bank ref: TXN-20260205-001

**Payment 2** (Pending, Not Overdue):
- Due date: 2026-02-20
- Payment date: null
- Customer: 李小華
- Space: B區-03
- Type: 月租
- Amount: NT$3,600
- Status: pending

**Payment 3** (Overdue):
- Due date: 2026-01-25
- Payment date: null
- Customer: 陳大同
- Space: A區-05
- Type: 月租
- Amount: NT$4,200
- Status: pending
- Days overdue: 21 days (if today is 2026-02-15)
- Badge: "⚠️ 逾期 21 天" (red)

**Payment 4** (Voided):
- Due date: 2026-02-01
- Payment date: null
- Customer: 張小美
- Space: C區-02
- Type: 月租
- Amount: ~~NT$3,800~~
- Status: voided
- Notes: "合約於 2026-02-10 終止"

### Search Examples
**Search: "王"** → Matches "王小明", "王大同"
**Search: "A-01"** → Matches space "A區-01"
**Search: "TXN-202"** → Matches bank_ref "TXN-20260205-001"

### Filter Examples
**Status: "逾期未付"** → Only pending payments where current_date > due_date
**Date Range: 2026-02-01 to 2026-02-28** → Due dates in February
**Amount: NT$3,500 to NT$4,000** → Payments between 3500-4000 inclusive

### Combined Filter
**Search: "王" + Status: "待付款" + Date: 本月 + Amount: >3000**
- Result: Pending payments for customers with "王" in name, due this month, amount > 3000

### Summary Stats (Sample)
- 待付款總額: NT$45,600 (15筆)
- 已付款總額 (本月): NT$128,000 (32筆)
- 逾期付款: 5筆 (總額 NT$18,000)
- 本月收款: NT$95,000 (24筆)

### Empty State
**No payments**: "目前沒有付款記錄" + "新增合約" button → Redirect to `/admin/agreements/new`
**No results**: Search "XYZ" → "找不到符合條件的付款記錄" + "清除篩選" button
