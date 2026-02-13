# US-CUST-004: Search and Filter Customers

**Priority**: Must Have | **Phase**: Phase 1 | **Sprint**: Sprint 2 (Weeks 3-4)
**Domain**: Customer Management | **Epic**: Customer List Management

## User Story
As a parking lot admin, I want to search and filter the customer list, so that I can quickly find specific customers or view customers by criteria (e.g., customers with active agreements).

## Acceptance Criteria
- **AC1**: Search bar at top of customer list page, placeholder: "搜尋姓名、電話或 Email"
- **AC2**: Search is case-insensitive, partial match on: name, phone, contact_phone, email
- **AC3**: Search updates results dynamically (debounced 300ms after typing stops)
- **AC4**: Filter dropdown: "全部客戶" (default), "有活躍合約", "無合約記錄"
- **AC5**: "有活躍合約": Show only customers with `active_agreement_count > 0`
- **AC6**: "無合約記錄": Show only customers with `active_agreement_count = 0`
- **AC7**: Sort dropdown: "最新建立" (default), "最舊建立", "姓名 A-Z", "姓名 Z-A", "活躍合約數 (高至低)"
- **AC8**: Pagination: Show 20 customers per page, page numbers at bottom, "上一頁" / "下一頁" buttons
- **AC9**: Result count displayed: "顯示 1-20 筆，共 156 筆客戶" (updates based on filters)
- **AC10**: Empty state: If no results → "找不到符合條件的客戶" with "清除篩選" button
- **AC11**: Clear button ("清除") visible when search/filters applied → Resets to default (all customers, newest first)

## Business Rules
- **Search Scope**: name, phone (with or without hyphens), contact_phone (with or without hyphens), email
- **Search Behavior**:
  - "王" → Matches "王小明", "王大同"
  - "0912" → Matches "0912-345-678"
  - "wang" → Matches "wang@example.com"
- **Filter Logic**: Search AND filter (both applied together)
  - Search "王" + Filter "有活躍合約" → Customers with name containing "王" AND active_agreement_count > 0
- **Default State**: All customers, sorted by newest first (created_at DESC)
- **Performance**: Search/filter should run server-side (not client-side filtering)
- **Case-Insensitive**: Search "WANG", "wang", "Wang" all match "wang@example.com"
- **Pagination Persistence**: Page number resets to 1 when search/filter changes

## UI Requirements
**Page**: 客戶管理 - 列表 (see 09-ui-ux/README.md, `/admin/customers`)
**Layout**: Search bar + filter/sort controls + table + pagination

### Search Bar
- Position: Top-left, above table
- Width: 300px
- Icon: Magnifying glass (left side)
- Placeholder: "搜尋姓名、電話或 Email"
- Clear button (×) appears when text entered

### Filter & Sort Controls
- Position: Top-right, same row as search bar
- Filter dropdown: "全部客戶" | "有活躍合約" | "無合約記錄"
- Sort dropdown: "最新建立" | "最舊建立" | "姓名 A-Z" | "姓名 Z-A" | "活躍合約數 (高至低)"
- "清除" button: Visible when non-default filters/search applied

### Table
- Columns: 姓名 | 電話 | Email | 活躍合約數 | 建立日期 | 操作
- Row click → Navigate to customer detail
- Active agreement count badge: "2" (green) if > 0, "0" (gray) if 0

### Pagination
- Position: Bottom-right of table
- Format: "顯示 1-20 筆，共 156 筆客戶"
- Controls: "上一頁" | 1 2 3 ... 8 | "下一頁"
- Disabled states: "上一頁" disabled on page 1, "下一頁" disabled on last page

### Empty State
- Icon: Search icon or empty box
- Message: "找不到符合條件的客戶"
- Subtext: "請嘗試調整搜尋條件或篩選器"
- Button: "清除篩選"

## Source
init_draft.md line 94 (customer list UI), CLAUDE.md (search patterns)

## Dependencies
US-CUST-001 (customer data exists), US-LOC-001 (Traditional Chinese UI), US-UI-003 (Customer List Page - to be written)

## Test Data
**Search by Name**:
- Search: "王" → Results: 王小明, 王大同, 王小華 (3 matches)
- Search: "李" → Results: 李小華, 李大明 (2 matches)

**Search by Phone**:
- Search: "0912" → Results: All customers with phone starting 0912
- Search: "345" → Results: Customers with "345" in phone (e.g., 0912-345-678)

**Search by Email**:
- Search: "example.com" → Results: All customers with @example.com email
- Search: "wang" → Results: wang@example.com (name "王小明" also matches if name search enabled)

**Filter: 有活躍合約**:
- Results: Only customers with active_agreement_count > 0
- Example: 王小明 (2 agreements), 陳大同 (1 agreement)
- Excludes: 李小華 (0 agreements)

**Filter: 無合約記錄**:
- Results: Only customers with active_agreement_count = 0
- Example: 李小華, 張小美
- Excludes: 王小明, 陳大同

**Combined Search + Filter**:
- Search: "王" + Filter: "有活躍合約"
- Results: 王小明 (has agreements) ✅
- Excludes: 王大同 (no agreements) ❌

**Sort by Name A-Z**:
- Results: 李小華, 王大同, 王小明, 陳大同 (alphabetical by name)

**Sort by Active Agreement Count (High to Low)**:
- Results: 王小明 (2), 陳大同 (1), 李小華 (0), 張小美 (0)

**Pagination**:
- Total: 156 customers
- Page 1: Customers 1-20
- Page 2: Customers 21-40
- Page 8: Customers 141-156 (last page, only 16 customers)

**Empty State**:
- Search: "XYZ123" (no matches)
- Result: "找不到符合條件的客戶" + "清除篩選" button
