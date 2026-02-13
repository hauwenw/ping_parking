# US-CUST-001: Create/Register New Customer

**Priority**: Must Have | **Phase**: Phase 1 | **Sprint**: Sprint 2 (Weeks 3-4)
**Domain**: Customer Management | **Epic**: Customer CRUD

## User Story
As a parking lot admin, I want to register new customers with their contact information, so that I can create rental agreements and track customer relationships.

## Acceptance Criteria
- **AC1**: Admin clicks "新增客戶" button on customer list page → Modal form opens
- **AC2**: Form fields: 姓名 (name)*, 電話 (phone)*, 聯絡電話 (contact_phone), Email (email), 備註 (notes)
- **AC3**: Phone validation: Must be 10 digits starting with 09. Input auto-formatted with hyphens for display, stored without dashes (`09XXXXXXXX`). Error: "電話格式不正確 (09XX-XXX-XXX)"
- **AC4**: Email validation: If provided, must be valid email format, error: "Email 格式不正確"
- **AC5**: Uniqueness check: If same name + phone combination already exists → Error: "此姓名與電話組合已存在"
- **AC6**: Name validation: 2-50 characters, error: "姓名長度需介於 2-50 個字元"
- **AC7**: Click "儲存" → Creates customer, modal closes, customer list refreshes, success toast: "客戶已新增"
- **AC8**: Click "取消" → Modal closes without saving, no changes made
- **AC9**: Mutation logged to `system_logs`: `action='CREATE_CUSTOMER'`, `new_values={name, phone, email, notes}`

## Business Rules
- **Name + Phone as Unique Identifier**: The combination of name and phone uniquely identifies a customer. Two people sharing the same company phone (different names) can coexist.
- **Email Optional**: Not all customers have email addresses
- **NO National ID**: Must not collect Taiwan national ID numbers (privacy compliance per US-SEC-004)
- **Validation**: All validation happens client-side (immediate feedback) + server-side (security)
- **Auto-Generated ID**: UUID generated automatically by database
- **Created Timestamp**: `created_at` and `updated_at` set automatically
- **Initial Agreement Count**: `active_agreement_count = 0` for new customers

## UI Requirements
**Page**: 客戶管理 - 列表 (see 09-ui-ux/README.md, `/admin/customers`)
**Trigger**: "新增客戶" button (top-right of customer list page)
**Modal Form**:
- Title: "新增客戶"
- Fields:
  - 姓名 * (Text input, required, placeholder: "王小明")
  - 電話 * (Text input, required, placeholder: "0912-345-678", auto-format with hyphens)
  - 聯絡電話 (Text input, optional, placeholder: "0912-345-678", auto-format with hyphens, same validation as phone if provided)
  - Email (Text input, optional, placeholder: "example@example.com")
  - 備註 (Textarea, optional, placeholder: "客戶需求、偏好等備註", max 500 chars)
- Actions: "儲存" (primary button) | "取消" (secondary button)
- Validation: Inline error messages below each field

**Phone Input Behavior**:
- Auto-format as user types: `0912345678` → `0912-345-678`
- Allow paste of unformatted phone numbers
- Only allow digits and hyphens
- Max 12 characters (including hyphens)

## Source
init_draft.md line 65 (customers table), line 94 (UI), CLAUDE.md privacy rules

## Dependencies
US-LOC-001 (Traditional Chinese labels), US-LOC-002 (Taiwan phone format), US-AUDIT-002 (logging), US-SEC-004 (no national ID), US-UI-003 (Customer List Page - to be written)

## Test Data
**Valid Customer**:
- Name: "王小明", Phone: "0912-345-678", Email: "wang@example.com", Notes: "VIP客戶"
- Expected: Customer created successfully, ID generated (UUID)

**Valid Customer (No Email)**:
- Name: "李小華", Phone: "0923-456-789", Email: "", Notes: ""
- Expected: Customer created (email optional)

**Invalid Phone Format**:
- Phone: "12345" → Error: "電話格式不正確 (09XX-XXX-XXX)"
- Phone: "0812-345-678" → Error: "電話格式不正確 (09XX-XXX-XXX)" (must start with 09)

**Duplicate Name + Phone**:
- Name: "王小明", Phone: "0912-345-678" (same combination already exists)
- Expected: Error: "此姓名與電話組合已存在"

**Same Phone, Different Name (Allowed)**:
- Name: "王大明", Phone: "0912-345-678" (different name, same phone as 王小明)
- Expected: Customer created successfully (composite unique allows this)

**Invalid Name**:
- Name: "王" (1 char) → Error: "姓名長度需介於 2-50 個字元"
- Name: "" (empty) → Error: "姓名為必填欄位"

**Invalid Email**:
- Email: "notanemail" → Error: "Email 格式不正確"
- Email: "test@" → Error: "Email 格式不正確"
