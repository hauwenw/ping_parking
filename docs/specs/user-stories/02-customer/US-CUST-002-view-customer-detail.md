# US-CUST-002: View Customer Detail

**Priority**: Must Have | **Phase**: Phase 1 | **Sprint**: Sprint 2 (Weeks 3-4)
**Domain**: Customer Management | **Epic**: Customer CRUD

## User Story
As a parking lot admin, I want to view complete customer details including agreement history, so that I can understand the customer's rental relationship and manage their account effectively.

## Acceptance Criteria
- **AC1**: Customer detail page displays: ID (UUID with copy icon), Name, Phone, Email (if provided), Notes, Active Agreement Count badge, Created Date, Last Updated Date
- **AC2**: Active agreement count shown as badge: "王小明 (2)" if 2 active agreements, no badge if 0
- **AC3**: Tabbed interface: "基本資料" (default tab), "合約記錄", "候補記錄" (Phase 2 - disabled/hidden)
- **AC4**: "基本資料" tab displays customer info in card format with "編輯" button (top-right)
- **AC5**: "合約記錄" tab displays agreement table: Space, License Plates (first + count), Type, Dates (Start/End), Status, Actions (查看)
- **AC6**: Click agreement row in table → Navigate to agreement detail page (`/admin/agreements/:agreementId`)
- **AC7**: Empty state: If customer has no agreements → Show message "此客戶目前沒有合約記錄" with "新增合約" button
- **AC8**: URL pattern: `/admin/customers/:customerId` (customerId is UUID)
- **AC9**: Breadcrumb: `首頁 > 客戶管理 > [Customer Name]`
- **AC10**: "新增合約" button (top-right action bar) → Navigate to agreement creation form with customer pre-selected

## Business Rules
- **UUID Display**: Show first 8 characters with "..." and copy icon (full UUID on hover tooltip)
- **Active Agreement Count**: Computed dynamically from `agreements` table where `status='active'` AND `customer_id=:id`
- **Agreement History**: Show all agreements (pending/active/expired/terminated) in reverse chronological order (newest first)
- **License Plate Display**: In agreement table, show first plate + count: "ABC-1234 (+1 more)" if multiple plates
- **Cross-Navigation**: Customer name clickable in agreement detail → back to customer detail
- **Access Control**: Admin-only page (requires authentication per US-SEC-001)

## UI Requirements
**Page**: 客戶詳情 (see 09-ui-ux/README.md, `/admin/customers/:customerId`)
**Layout**: Card-based sections with tabs

### Header Section
- Customer name with active count badge: "王小明 (2)"
- Action buttons: "編輯" | "新增合約"
- Breadcrumb navigation

### Tab 1: 基本資料 (Customer Info Card)
- **Fields displayed**:
  - 客戶 ID: `cust-abc1...` (copy icon)
  - 姓名: 王小明
  - 電話: 0912-345-678
  - 聯絡電話: 0933-111-222 (or "未提供" if null)
  - Email: wang@example.com (or "未提供" if null)
  - 備註: [Notes text or "無備註"]
  - 活躍合約數: 2
  - 建立日期: 2026年1月15日
  - 最後更新: 2026年1月20日

### Tab 2: 合約記錄 (Agreement Table)
- **Columns**: 車位 | 車牌 | 類型 | 開始日期 | 結束日期 | 狀態 | 操作
- **Row example**: A區-01 | ABC-1234 (+1 more) | 月租 | 2026-02-01 | 2026-03-01 | 進行中 (green badge) | 查看 (link)
- **Sorting**: Newest first (by start_date DESC)
- **Empty state**: "此客戶目前沒有合約記錄" + "新增合約" button

### Tab 3: 候補記錄 (Phase 2)
- Disabled/hidden in Phase 1
- Future: Show waiting list entries for this customer

## Source
init_draft.md line 94 (UI navigation), CLAUDE.md (cross-page navigation)

## Dependencies
US-CUST-001 (customer must exist), US-AGREE-001 (agreement data), US-AGREE-005 (agreement detail page), US-AGREE-008 (cross-navigation), US-UI-004 (Customer Detail Page - to be written)

## Test Data
**Customer with Active Agreements**:
- Customer: 王小明 (cust-001)
- Phone: 0912-345-678
- Email: wang@example.com
- Active Agreements: 2
- Agreements table shows:
  1. A區-01, ABC-1234 (+1 more), 月租, 2026-02-01 至 2026-03-01, 進行中
  2. B區-05, XYZ-5678, 月租, 2026-01-15 至 2026-02-15, 進行中

**Customer with No Agreements**:
- Customer: 李小華 (cust-002)
- Phone: 0923-456-789
- Email: null
- Active Agreements: 0
- Agreement tab shows: "此客戶目前沒有合約記錄" + "新增合約" button

**Customer with Mixed Agreement Statuses**:
- Customer: 陳大同 (cust-003)
- Active: 1 (進行中, green)
- Expired: 2 (已過期, gray)
- Terminated: 1 (已終止, dark gray)
- Table shows all 4 agreements, sorted newest first

**Navigation Flow**:
- Customer list → Click "王小明" row → Customer detail page
- Customer detail → Click agreement row → Agreement detail
- Agreement detail → Click customer name → Back to customer detail
