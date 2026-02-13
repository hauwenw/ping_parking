# US-AGREE-005: View Agreement Details

**Priority**: Must Have | **Phase**: Phase 1 | **Sprint**: Sprint 3 (Weeks 5-6)
**Domain**: Agreement Management | **Epic**: Agreement CRUD

## User Story
As a parking lot admin, I want to view complete agreement details including customer, space, payment, and status information, so that I can quickly understand the rental contract and its current state.

## Acceptance Criteria
- **AC1**: Agreement detail page displays: ID (UUID with copy), Status badge (進行中/待生效/已過期/已終止), Customer info (linked), Space info (linked with tags), License plates (all plates as badges or comma-separated list), Type, Dates (Start/End/Remaining days), Pricing (amount + breakdown), Payment (status + link), Audit trail (created/updated timestamps)
- **AC2**: Active agreement shows action buttons: 編輯, 終止合約, 查看付款
- **AC3**: Expired agreement: status badge gray, hide edit/terminate buttons, show 續約 button (see Renewal Flow below)
- **AC4**: Cross-navigation links work: customer name → customer detail, space name → space detail, payment link → payment detail
- **AC5**: URL: `/admin/agreements/:agreementId`

## Renewal Flow (續約)

**Trigger**: Admin clicks "續約" button on an expired (or terminated) agreement detail page.

**Behavior**: Navigates to agreement creation form (`/admin/agreements/new?renewFrom=:agreementId`) with pre-filled fields:
- **Customer**: Pre-selected (editable)
- **Space**: Pre-selected (editable — space may have been reassigned since expiry)
- **License Plates**: Carried over from old agreement (editable)
- **Agreement Type**: Same as old agreement (editable)
- **Start Date**: Defaults to **today** if old end_date is in the past; defaults to **day after end_date** if renewing at or before expiry

**Price Handling**:
- Price recalculated using **current** space/tag rates (not the old agreement's price)
- If price differs from old agreement, show info banner: "提醒：此車位目前價格為 NT$4,000（前次合約為 NT$3,600）"

**Validation**: Normal agreement creation rules apply (date overlap check via US-AGREE-004). If the space is occupied by another agreement, admin sees the overlap error and can change the space.

**No formal link**: The new agreement does not store a reference to the old one (keep schema simple for Phase 1).

**After save**: Redirect to the new agreement detail page with success toast: "續約合約已建立"

## Business Rules
- Read-only for expired/terminated agreements (edit and terminate buttons hidden)
- Cross-navigation to all related entities
- Real-time status (auto-updated based on current date vs end_date)
- Payment link always shown (auto-generated on creation)

## UI Requirements
**Page Structure**: See `09-ui-ux/README.md` for Agreement Detail page definition (`/admin/agreements/:agreementId`)
**Layout**: Card-based sections: Header (ID/status/actions), Customer & Space (2-column), Agreement Details, Pricing, Payment, Audit
**License Plates Display**: Show all plates as badges (e.g., "ABC-1234" "XYZ-9999") or comma-separated: "ABC-1234, XYZ-9999"
**Color Coding**: Pending=blue, Active=green, Expired=gray, Terminated=dark gray

## Source
init_draft.md lines 95-96 (cross-page navigation) | CLAUDE.md

## Dependencies
US-AGREE-001, US-CUST-001, US-SPACE-001, US-PAY-002, US-LOC-003, US-LOC-004

## Test Data

**Active Agreement**:
Customer: 王小明 | Space: A區-01, tags=['有屋頂'] | License Plates: ['ABC-1234', 'XYZ-9999'] | Type: Monthly | Start: 2026-02-01, End: 2026-03-01 | Price: NT$3,600 | Status: Active (14 days remaining)

**Renewal Flow — Price Changed**:
1. Old agreement: A區-01, Monthly, NT$3,600 (expired 2026-03-01)
2. Space price since updated to NT$4,000
3. Click 續約 → Form pre-filled, start date = today
4. Price shows NT$4,000 with banner: "提醒：此車位目前價格為 NT$4,000（前次合約為 NT$3,600）"

**Renewal Flow — Space Taken**:
1. Old agreement: A區-01, expired
2. A區-01 now has active agreement for another customer
3. Click 續約 → Form pre-filled with A區-01
4. Admin changes start date → Overlap error → Admin picks different space A區-05
