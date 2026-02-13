# US-CUST-003: Edit Customer Information

**Priority**: Must Have | **Phase**: Phase 1 | **Sprint**: Sprint 2 (Weeks 3-4)
**Domain**: Customer Management | **Epic**: Customer CRUD

## User Story
As a parking lot admin, I want to edit customer contact information and notes, so that I can keep customer records up-to-date when their details change.

## Acceptance Criteria
- **AC1**: Admin clicks "編輯" button on customer detail page → Modal form opens with pre-filled current values
- **AC2**: Form fields: 姓名 (name)*, 電話 (phone)*, 聯絡電話 (contact_phone), Email (email), 備註 (notes) - same as create form
- **AC3**: All validation rules same as US-CUST-001: phone format, email format, name length, phone uniqueness
- **AC4**: Name + phone uniqueness check excludes current customer: Can keep same name+phone, error only if the new name+phone combination matches a different customer
- **AC5**: Changed fields highlighted or marked (optional UX enhancement)
- **AC6**: Click "儲存" → Updates customer, modal closes, detail page refreshes, success toast: "客戶資料已更新"
- **AC7**: Click "取消" → Modal closes without saving, no changes made
- **AC8**: Mutation logged to `system_logs`: `action='UPDATE_CUSTOMER'`, `old_values={...}`, `new_values={...}` (only changed fields)
- **AC9**: `updated_at` timestamp automatically set to current time
- **AC10**: Customer ID and created_at are immutable (not editable)

## Business Rules
- **Editable Fields**: name, phone, contact_phone, email, notes
- **Immutable Fields**: id, created_at (displayed but greyed out/disabled)
- **Name + Phone Uniqueness**: New name+phone combination must be unique OR same as current (allow unchanged)
- **No Deletion**: Customer records are never deleted. No delete button in UI. Data preserved for historical reference and audit trail integrity.
- **Agreement Impact**: Editing customer does NOT affect existing agreements (customer_id relationship preserved)
- **Validation**: Same rules as create (US-CUST-001)
- **Audit Trail**: Log old and new values for all changed fields

## UI Requirements
**Page**: 客戶詳情 (see 09-ui-ux/README.md, `/admin/customers/:customerId`)
**Trigger**: "編輯" button (top-right of customer detail page, next to "新增合約")
**Modal Form**:
- Title: "編輯客戶資料"
- Fields: Same as create form (US-CUST-001) but pre-filled with current values
- Immutable fields displayed as:
  - 客戶 ID: cust-abc1... (greyed out, not editable)
  - 建立日期: 2026年1月15日 (greyed out)
- Actions: "儲存" (primary) | "取消" (secondary)
- Validation: Same as create, inline error messages

**Pre-fill Behavior**:
- Load current customer data into form fields
- Phone: Display with hyphens (0912-345-678)
- Email: Display current email or empty if null
- Notes: Display current notes or empty if null

**Save Behavior**:
- Compare old vs new values
- Only send changed fields to API (partial update)
- If no fields changed → Show info message: "沒有變更需要儲存"

## Source
CLAUDE.md (customer management), init_draft.md line 65

## Dependencies
US-CUST-001 (validation rules), US-CUST-002 (detail page context), US-LOC-002 (phone format), US-AUDIT-002 (logging)

## Test Data
**Successful Edit (Name Only)**:
- Original: Name="王小明", Phone="0912-345-678", Email="wang@example.com"
- Edit: Name="王大明" (change name only)
- Expected: Name updated, phone/email unchanged, `updated_at` updated, logged

**Successful Edit (Phone Change)**:
- Original: Phone="0912345678"
- Edit: Phone="0913999888" (new unique phone)
- Expected: Phone updated, logged with old="0912345678", new="0913999888"

**Name + Phone Conflict (Different Customer)**:
- Customer A: Name="王小明", Phone="0912345678"
- Edit Customer B: Name="王小明", Phone="0912345678" (same name+phone as Customer A)
- Expected: Error: "此姓名與電話組合已存在"

**Same Phone, Different Name (No Conflict)**:
- Customer A: Name="王小明", Phone="0912345678"
- Edit Customer B: Name="李小華", Phone="0912345678" (same phone, different name)
- Expected: No error, update allowed

**Same Name + Phone (No Conflict - Unchanged)**:
- Original: Name="王小明", Phone="0912345678"
- Edit: Name="王小明", Phone="0912345678" (keep same)
- Expected: No error, update allowed

**Invalid Phone Format**:
- Edit: Phone="12345"
- Expected: Error: "電話格式不正確 (09XX-XXX-XXX)"

**Clear Optional Email**:
- Original: Email="wang@example.com"
- Edit: Email="" (clear email)
- Expected: Email set to null, saved successfully

**No Changes**:
- Open edit form, change nothing, click "儲存"
- Expected: Info message: "沒有變更需要儲存", modal closes without API call

**Audit Log Example**:
```json
{
  "action": "UPDATE_CUSTOMER",
  "table": "customers",
  "record_id": "cust-001",
  "old_values": {"name": "王小明", "phone": "0912345678"},
  "new_values": {"name": "王大明", "phone": "0913999888"},
  "user_id": "admin-001",
  "timestamp": "2026-01-25T10:30:00Z"
}
```
