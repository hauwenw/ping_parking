# US-PAY-002: Record Payment (Manual Completion)

**Priority**: Must Have | **Phase**: Phase 1 | **Sprint**: Sprint 3 (Weeks 5-6)
**Domain**: Payment Management | **Epic**: Payment Tracking

## User Story
As a parking lot admin, I want to manually record when a customer has paid, so that I can track which agreements have been paid and which are outstanding.

## Acceptance Criteria

### Payment Recording Flow
- **AC1**: Admin navigates to payment detail page (from agreement detail or payment list) → Payment shows "記錄付款" button if status='pending'
- **AC2**: Click "記錄付款" → Modal opens with form fields: 付款日期* (date), 銀行參考號碼* (text), 備註 (optional textarea)
- **AC3**: Payment date defaults to today, editable to past or future dates
- **AC4**: Bank reference required (error: "請填寫銀行參考號碼"), max 50 characters, alphanumeric + hyphens
- **AC5**: On save → Payment status changes to 'completed', payment_date and bank_ref stored, modal closes, toast: "付款已記錄"
- **AC6**: After completion → "記錄付款" button hidden, payment detail shows: 付款日期, 銀行參考號碼, status badge changes to "已付款 (completed, green)"
- **AC7**: Completed payment cannot be reverted to pending (immutable transition)
- **AC8**: Action logged to system_logs: action='COMPLETE_PAYMENT', old_values={status: 'pending'}, new_values={status: 'completed', payment_date, bank_ref}

### Validation Rules
- **AC9**: Payment date cannot be before agreement start_date (error: "付款日期不可早於合約開始日期")
- **AC10**: Bank reference uniqueness check: If same bank_ref already exists for different payment → Warning (not error): "此銀行參考號碼已被使用，請確認"
- **AC11**: Cannot record payment if agreement is terminated and payment is voided (button not shown)

### Agreement Integration
- **AC12**: After payment recorded → Agreement detail page shows payment status as "已付款" with green checkmark
- **AC13**: Payment link on agreement detail → Click opens payment detail showing completion info

## Business Rules

### Payment Completion
- **One-way transition**: pending → completed (no reversal to pending)
- **Manual process**: No automatic payment gateway in Phase 1 — admin enters offline payment info
- **Bank reference**: Used for reconciliation with bank statements (not validated against external system)
- **Payment date flexibility**: Can record past payments (backdated) or future-dated payments (e.g., post-dated checks)

### Bank Reference Format
- Alphanumeric + hyphens: `TXN-20260215-001`, `BANK123456`, `CHQ-2026-001`
- Not enforced to specific format (banks use different formats)
- Admin responsible for accuracy

### Immutability After Completion
- Once payment is completed, status cannot change to pending or voided
- Amount can still be edited (via US-PAY-001) with logged reason
- Payment date and bank ref are editable after completion (via edit payment detail)

### Voided Payments
- If payment status='voided' (agreement terminated), "記錄付款" button not shown
- Voided payments cannot be completed (must create new agreement if customer wants to resume)

## UI Requirements

### Payment Detail Page - Record Payment Button
**Location**: `/admin/payments/:paymentId`

**Button Display Rules**:
- Visible: status='pending'
- Hidden: status='completed' or status='voided'
- Position: Top-right action area, next to "編輯金額"
- Style: Primary action button
- Label: "記錄付款"

### Record Payment Modal
**Trigger**: Click "記錄付款" button

**Form Fields**:
- **付款日期 * (Payment Date)**:
  - Type: Date picker
  - Default: Today
  - Validation: Required, cannot be before agreement start_date
  - Format: YYYY-MM-DD (ISO for input), displayed as YYYY年MM月DD日

- **銀行參考號碼 * (Bank Reference)**:
  - Type: Text input
  - Placeholder: "例如：TXN-20260215-001"
  - Max length: 50 characters
  - Validation: Required, alphanumeric + hyphens
  - Uniqueness warning (not blocking): "⚠️ 此銀行參考號碼已被使用，請確認"

- **備註 (Notes)**:
  - Type: Textarea
  - Optional
  - Max length: 200 characters
  - Placeholder: "例如：現金付款、轉帳付款等"

**Validation Errors**:
- Empty payment date: "付款日期為必填欄位"
- Payment date before agreement start: "付款日期不可早於合約開始日期 (2026-02-01)"
- Empty bank reference: "請填寫銀行參考號碼"
- Invalid bank reference format: "銀行參考號碼格式不正確 (僅限英數字與連字號)"

**Actions**:
- "儲存" (primary) → Validate, update payment, log, close modal, show toast
- "取消" (secondary) → Close modal without changes

**Success State**:
- Toast notification: "付款已記錄"
- Modal closes
- Payment detail page refreshes showing completed status

### Payment Detail Page - Completed State
**After recording payment, display**:
- Status badge: "已付款" (green)
- 付款日期: 2026年02月15日
- 銀行參考號碼: TXN-20260215-001 (with copy icon)
- 備註: (if provided)
- "記錄付款" button → Hidden
- "編輯付款資訊" button → Visible (for editing date/bank_ref if needed)

### Agreement Detail Page - Payment Section
**Payment status indicator**:
- Pending: "待付款" (yellow badge) + "記錄付款" button
- Completed: "已付款" (green badge with ✓) + "已於 2026年02月15日 付款"
- Voided: "已作廢" (gray badge) + void reason

## Implementation Notes

### Database Update
```typescript
async function recordPayment(
  paymentId: string,
  paymentDate: Date,
  bankRef: string,
  notes?: string
) {
  // Validate payment exists and is pending
  const payment = await db.payments.findById(paymentId);

  if (payment.status !== 'pending') {
    throw new Error('只能記錄待付款狀態的付款');
  }

  // Validate payment date not before agreement start
  const agreement = await db.agreements.findById(payment.agreement_id);
  if (paymentDate < agreement.start_date) {
    throw new Error('付款日期不可早於合約開始日期');
  }

  // Check for duplicate bank reference (warning only)
  const duplicate = await db.payments.findOne({
    bank_ref: bankRef,
    id: { $ne: paymentId }
  });

  if (duplicate) {
    console.warn(`Duplicate bank reference: ${bankRef}`);
    // Allow to proceed but log warning
  }

  // Update payment
  await db.payments.update(paymentId, {
    status: 'completed',
    payment_date: paymentDate,
    bank_ref: bankRef,
    notes: notes,
    updated_at: new Date()
  });

  // Log to audit
  await logToAudit('COMPLETE_PAYMENT', {
    payment_id: paymentId,
    old_values: { status: 'pending' },
    new_values: { status: 'completed', payment_date: paymentDate, bank_ref: bankRef }
  });

  return payment;
}
```

### Bank Reference Uniqueness Check (Non-Blocking)
```typescript
async function checkBankRefDuplicate(bankRef: string, excludePaymentId: string) {
  const existing = await db.payments.findOne({
    bank_ref: bankRef,
    id: { $ne: excludePaymentId }
  });

  return {
    isDuplicate: !!existing,
    existingPayment: existing ? {
      id: existing.id,
      agreement_id: existing.agreement_id,
      customer_name: existing.agreement.customer.name
    } : null
  };
}
```

## Source
init_draft.md line 28 (manual offline payment recording), CLAUDE.md payment lifecycle

## Dependencies
- US-PAY-001 (payment lifecycle - defines payment structure)
- US-AGREE-001 (agreement must exist)
- US-AUDIT-002 (audit logging)
- US-LOC-003 (TWD currency format)
- US-LOC-004 (Taiwan date format)

## Test Data

### Successful Payment Recording
**Payment (before)**:
- ID: pay-001
- Agreement: agr-001 (start_date: 2026-02-01)
- Amount: NT$4,000
- Due date: 2026-02-01
- Status: pending

**Admin Records Payment**:
- Payment date: 2026-02-15
- Bank reference: TXN-20260215-001
- Notes: "銀行轉帳"

**Payment (after)**:
- Status: completed
- Payment date: 2026-02-15
- Bank ref: TXN-20260215-001
- Notes: "銀行轉帳"

### Backdated Payment (Past Date)
**Scenario**: Customer paid last week but admin records today
- Agreement start: 2026-02-01
- Today: 2026-02-15
- Admin records: payment_date = 2026-02-08 (backdated)
- Result: Allowed, payment recorded with historical date

### Validation Error - Payment Date Before Start
**Payment**:
- Agreement start_date: 2026-02-15
- Admin tries: payment_date = 2026-02-10 (before start)
- Result: Error "付款日期不可早於合約開始日期 (2026-02-15)"

### Duplicate Bank Reference Warning
**Scenario**: Admin accidentally uses same bank ref twice
- Payment A: bank_ref = "TXN-123456" (completed)
- Payment B: Admin tries bank_ref = "TXN-123456"
- Result: Warning shown "⚠️ 此銀行參考號碼已被使用 (客戶: 王小明，合約: A-01)，請確認"
- Admin can proceed if intentional (e.g., batch payment under one transaction)

### Invalid Bank Reference Format
**Admin Input**: bank_ref = "TXN 123 456" (contains spaces)
- Result: Error "銀行參考號碼格式不正確 (僅限英數字與連字號)"

**Valid formats**:
- "TXN-20260215-001" ✅
- "BANK123456" ✅
- "CHQ-2026-001" ✅
- "20260215" ✅

### Cannot Record Voided Payment
**Payment**:
- Status: voided (agreement terminated)
- UI: "記錄付款" button hidden
- Admin opens payment detail → Shows "已作廢 (合約終止)" badge
- No action available

### Cannot Revert Completed Payment
**Payment**:
- Status: completed
- Payment date: 2026-02-15
- Admin tries to change status back to pending → No UI option available
- Status field immutable after completion
