# US-CUST-005: Link Customer to Agreement

**Priority**: Must Have | **Phase**: Phase 1 | **Sprint**: Sprint 2 (Weeks 3-4)
**Domain**: Customer Management | **Epic**: Cross-Domain Integration

## User Story
As a parking lot admin, I want to quickly create a new agreement from the customer detail page, so that I can efficiently allocate parking spaces to existing customers without searching for them again.

## Acceptance Criteria
- **AC1**: "新增合約" button visible on customer detail page (top-right action bar, next to "編輯")
- **AC2**: Click "新增合約" → Navigate to agreement creation form (`/admin/agreements/new?customerId=:customerId`)
- **AC3**: Agreement form pre-fills: Customer dropdown auto-selected with current customer, field disabled (greyed out but value visible)
- **AC4**: User completes rest of form: Space selection, License plates, Agreement type, Start date
- **AC5**: After successful agreement creation → Redirect back to customer detail page with success toast: "合約已新增"
- **AC6**: Customer detail "合約記錄" tab auto-refreshes to show new agreement at top of list
- **AC7**: Customer's active agreement count badge updates if new agreement status is "active"
- **AC8**: Breadcrumb on agreement form shows origin: `首頁 > 客戶管理 > [Customer Name] > 新增合約`

## Business Rules
- **Pre-filled Customer**: `customer_id` parameter passed via URL query string
- **Customer Field Locked**: Customer selection field is disabled (cannot change customer in this flow)
- **Navigation Flow**: Customer detail → Agreement form → Back to customer detail (after save)
- **Empty Agreement List**: "新增合約" button also shown in empty state message of "合約記錄" tab
- **Validation**: All agreement validation rules from US-AGREE-001 still apply
- **Cancel Behavior**: If user clicks "取消" on agreement form → Return to customer detail page

## UI Requirements
**Trigger Page**: 客戶詳情 (see 09-ui-ux/README.md, `/admin/customers/:customerId`)
**Target Page**: 合約管理 - 新增 (agreement creation form)

### Customer Detail Page Button
- Position: Top-right action bar, next to "編輯" button
- Label: "新增合約"
- Icon: Plus icon (optional)
- Style: Primary action button

### Agreement Creation Form (Pre-filled)
- **Customer Field**:
  - Label: "客戶 *"
  - Value: "王小明 (0912-345-678)" (name + phone)
  - State: Disabled (greyed out), value visible but not editable
  - Hidden input: `customer_id` (UUID)
- **Other Fields**: Space, License plates, Type, Start date (all enabled, no pre-fill)
- **Breadcrumb**: `首頁 > 客戶管理 > 王小明 > 新增合約`
- **Cancel Button**: Returns to customer detail page

### After Save Success
- Redirect: `/admin/customers/:customerId?tab=agreements` (open "合約記錄" tab)
- Toast: "合約已新增"
- Table: New agreement appears at top (newest first)
- Badge: Active count updates if new agreement is active

### Empty State Alternative
**在 "合約記錄" Tab Empty State**:
- Message: "此客戶目前沒有合約記錄"
- Button: "新增合約" (same functionality as top-right button)

## Source
init_draft.md line 94 (cross-page navigation), CLAUDE.md (workflow efficiency)

## Dependencies
US-CUST-002 (customer detail page), US-AGREE-001 (agreement creation), US-AGREE-008 (cross-navigation), US-UI-004 (Customer Detail Page), US-UI-006 (Agreement Form Page - to be written)

## Test Data
**Successful Flow**:
1. Navigate to: Customer detail page for "王小明" (cust-001)
2. Current state: 王小明 has 1 active agreement
3. Click "新增合約" button
4. Redirected to: `/admin/agreements/new?customerId=cust-001`
5. Form shows: Customer="王小明 (0912-345-678)" (disabled)
6. Fill form: Space=A-02, License Plate=DEF-5678, Type=Monthly, Start=2026-02-15
7. Click "儲存"
8. Redirected to: `/admin/customers/cust-001?tab=agreements`
9. Toast: "合約已新增"
10. Table: New agreement "A-02, DEF-5678, 月租, 2026-02-15..." appears at top
11. Badge: "王小明 (2)" (count increased from 1 to 2)

**Cancel Flow**:
1. Customer detail → Click "新增合約"
2. Agreement form opens with customer pre-filled
3. Start filling form, then click "取消"
4. Redirected back to: `/admin/customers/cust-001`
5. No agreement created, no changes made

**Empty State Flow**:
1. Navigate to: Customer detail for "李小華" (cust-002, no agreements)
2. "合約記錄" tab shows: "此客戶目前沒有合約記錄"
3. Two options to create agreement:
   - Top-right "新增合約" button
   - "新增合約" button in empty state message
4. Both buttons lead to same agreement form with customer pre-filled

**URL Parameter Handling**:
- URL: `/admin/agreements/new?customerId=cust-001`
- Query param `customerId` parsed on page load
- Customer dropdown auto-selected and disabled
- If `customerId` invalid/missing → Show error: "客戶不存在" + redirect to customer list

**Breadcrumb Navigation**:
- Click "客戶管理" in breadcrumb → Return to customer list
- Click "王小明" in breadcrumb → Return to customer detail
- Click "首頁" → Return to dashboard
