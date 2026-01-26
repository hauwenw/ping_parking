# US-AGREE-008: Cross-Page Navigation (Customer ↔ Agreement ↔ Payment)

**Priority**: Must Have | **Phase**: Phase 1 | **Sprint**: Sprint 4 (Weeks 7-8)
**Domain**: Agreement Management | **Epic**: User Experience & Navigation

> **NOTE**: This is a first iteration spec written during domain planning. When detailed UI/UX stories (US-UI-001 through US-UI-008) are created, those specifications take precedence. See `09-ui-ux/README.md` for current page structure and navigation patterns.

## User Story
As a parking lot admin, I want to navigate seamlessly between related customer, agreement, and payment records, so that I can quickly find related information without searching.

## Acceptance Criteria
- **AC1**: Customer → Agreements: Customer detail shows "合約記錄" section (table: space, license plates, type, dates, status, actions), click row → agreement detail, active count badge: "王小明 (2)". License plates column shows first plate + count if multiple: "ABC-1234 (+1 more)"
- **AC2**: Agreement → Customer: Customer name is clickable link → customer detail, breadcrumb: 合約管理 > 合約詳情 > 王小明
- **AC3**: Agreement → Space: Space name clickable → space detail (or site management filtered)
- **AC4**: Agreement → Payment: Payment section shows status badge + "查看付款詳情" link → payment detail
- **AC5**: Payment → Agreement: Agreement section shows ID, customer, space + "查看合約詳情" link → agreement detail
- **AC6**: Payment → Customer: Customer name clickable or via agreement → customer
- **AC7**: Breadcrumbs on all pages: 首頁 > [Section] > [Detail]

## Business Rules
- Bidirectional links between all related entities
- Context preservation: Back button returns to list with filters
- Deep linking: All detail pages accessible via URL
- Access control: All links respect admin auth

## UI Requirements
**Page Structure**: See `09-ui-ux/README.md` for complete page inventory and URL structure
**Link Styling**: Blue underlined (hover: darker)
**Breadcrumbs**: Consistent pattern across pages
**Customer Detail Tabs**: 基本資料/合約記錄/候補記錄

## Source
init_draft.md lines 12, 95-96 (cross-page navigation)

## Dependencies
US-AGREE-005, US-CUST-002, US-PAY-003

## Test Data
Customer: 王小明 (cust-001) | Agreement 1: A區-01, License Plates: ['ABC-1234', 'XYZ-9999'], Active, Payment Paid | Navigation: Customer detail → Agreements tab (shows "ABC-1234 (+1 more)") → Agreement detail (shows all plates) → Payment detail → Back to agreement → Back to customer
