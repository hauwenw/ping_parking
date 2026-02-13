# US-PAY-001: Payment Lifecycle (Auto-Generate, Edit, Void on Termination)

**Priority**: Must Have | **Phase**: Phase 1 | **Sprint**: Sprint 3 (Weeks 5-6)
**Domain**: Payment Management | **Epic**: Payment Tracking

## User Story
As a parking lot admin, I want payments to be automatically created when agreements are made and properly handled when agreements are terminated, so that I can track revenue without manual payment entry for every agreement.

## Acceptance Criteria

### Auto-Generation on Agreement Creation
- **AC1**: When an agreement is created, system automatically generates one payment record with:
  - `amount` = agreement price (already includes tag effects per US-SPACE-003)
  - `due_date` = agreement start_date
  - `status` = 'pending'
  - `agreement_id` = link to the agreement
- **AC2**: Payment creation is atomic with agreement creation (same transaction)
- **AC3**: Payment record logged to `system_logs` with action='CREATE_PAYMENT', new_values={amount, due_date, agreement_id}

### Payment Amount Source
- **AC4**: Payment amount always equals the agreement price at creation time (single source of truth)
- **AC5**: If admin edits agreement price before saving → Generated payment uses the edited price
- **AC6**: Agreement price already reflects tag effects (per US-SPACE-003), so payment amount includes all pricing adjustments

### Payment Editing
- **AC7**: Admin can edit payment amount after creation via payment detail page → "編輯金額" button
- **AC8**: Edit modal shows: Original amount (greyed out), New amount (editable), Reason (required text field, max 200 chars)
- **AC9**: On save → Payment amount updated, reason stored in `adjustment_reason` field, logged to system_logs with old/new values
- **AC10**: Completed payments can still be edited (e.g., retroactive discount) but show warning: "此付款已完成，修改金額將影響財務記錄"

### Agreement Termination Impact
- **AC11**: When an agreement is terminated (status='terminated'), system checks payment status:
  - If payment status = 'pending' → Auto-set to 'voided', termination reason copied to payment notes
  - If payment status = 'completed' → No change (payment already received, keep record)
  - If payment status = 'voided' → No change (already voided)
- **AC12**: Voided payment displays with strikethrough amount and badge: "已作廢 (合約終止)"
- **AC13**: Payment void action logged to system_logs with action='VOID_PAYMENT', reason='agreement_terminated'

### Payment Status Lifecycle
- **AC14**: Payment status flow: `pending` → `completed` / `voided`
- **AC15**: Status transitions:
  - pending → completed: Admin manually records payment (US-PAY-002)
  - pending → voided: Agreement terminated OR admin manually voids
  - No other transitions allowed (no reactivation)
- **AC16**: Status badges: 待付款 (pending, yellow) / 已付款 (completed, green) / 已作廢 (voided, gray)

## Business Rules

### One Payment Per Agreement
- **No partial payments** in Phase 1: One agreement = one payment record
- Full amount must be paid at once (cannot split into installments)
- If customer needs partial payment, admin must create separate agreements for different periods

### Payment Amount Immutability (Except Manual Edit)
- Payment amount does NOT auto-update when:
  - Agreement price is edited after creation (payment stays original amount unless manually edited)
  - Space price changes (agreement price is immutable per US-SPACE-003)
  - Tag price changes (agreement price is immutable)
- Admin can manually edit payment amount with logged reason

### Voiding Rules
- **Auto-void**: Only happens on agreement termination, only affects pending payments
- **Manual void**: Admin can void any pending payment (future enhancement - not in Phase 1)
- **Completed payments**: Never auto-voided (financial record preservation)

### Financial Integrity
- All payment amount changes require audit log entry
- Voided payments remain in database (soft delete, not hard delete)
- Original amount preserved in audit log even after edits

## UI Requirements

### Payment Auto-Generation (Invisible to User)
- No UI for payment creation during agreement creation
- Payment automatically created in background
- Agreement detail page shows linked payment immediately after creation

### Payment Detail Page
**Location**: `/admin/payments/:paymentId` or modal from agreement detail

**Display Fields**:
- Payment ID (UUID, copyable)
- Status badge (待付款/已付款/已作廢)
- Amount: NT$3,600 (with strikethrough if voided: ~~NT$3,600~~)
- Original amount (if edited): NT$3,600 → NT$3,200 (with adjustment reason)
- Due date: 2026年02月01日
- Linked agreement: A區-01, 王小明 (clickable link)
- Payment date: (empty if pending, date if completed)
- Notes: (termination reason if voided, adjustment reason if edited)

**Action Buttons** (conditional):
- "編輯金額" (visible if status = pending or completed)
- "記錄付款" (visible if status = pending, goes to US-PAY-002 flow)
- No delete button (payments never deleted)

### Payment Amount Edit Modal
**Trigger**: "編輯金額" button on payment detail page

**Fields**:
- 原始金額: NT$3,600 (read-only, greyed out)
- 新金額 *: NT$ input (required, min=0)
- 調整原因 *: Textarea (required, max 200 chars, placeholder: "例如：客戶折扣、價格調整")

**Validation**:
- New amount must differ from current amount (error: "新金額與原金額相同")
- Reason required (error: "請填寫調整原因")

**Warning** (if payment status = completed):
- Icon + text: "⚠️ 此付款已完成，修改金額將影響財務記錄。請確認後再儲存。"

**Actions**:
- "儲存" (primary) → Update payment, log audit, close modal, toast: "付款金額已更新"
- "取消" (secondary) → Close modal without changes

### Agreement Termination (Auto-Void Display)
**Location**: Agreement detail page after termination

**Payment Section Shows**:
- Status: ~~待付款~~ → 已作廢 (with strikethrough transition)
- Amount: ~~NT$3,600~~ (strikethrough)
- Badge: "已作廢 (合約終止)"
- Notes: "合約於 2026年02月15日 終止 (管理員手動終止)"

## Implementation Notes

### Database Schema

**Payments table**:
```sql
CREATE TABLE payments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agreement_id UUID NOT NULL REFERENCES agreements(id),
  amount INTEGER NOT NULL CHECK (amount >= 0),
  original_amount INTEGER, -- NULL initially, set when first edited
  adjustment_reason TEXT CHECK (char_length(adjustment_reason) <= 200),
  due_date DATE NOT NULL,
  payment_date DATE, -- NULL until paid
  status TEXT NOT NULL CHECK (status IN ('pending', 'completed', 'voided')),
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_payments_agreement_id ON payments(agreement_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_due_date ON payments(due_date);
```

### Payment Auto-Creation (Triggered on Agreement Insert)
```typescript
async function createAgreement(data: AgreementInput) {
  // Start transaction
  const agreement = await db.agreements.insert({
    customer_id: data.customer_id,
    space_id: data.space_id,
    license_plates: data.license_plates,
    agreement_type: data.agreement_type,
    start_date: data.start_date,
    end_date: calculateEndDate(data.start_date, data.agreement_type),
    price: data.price, // Already calculated from space price
    status: 'active'
  });

  // Auto-generate payment
  const payment = await db.payments.insert({
    agreement_id: agreement.id,
    amount: agreement.price, // Same as agreement price
    due_date: agreement.start_date,
    status: 'pending'
  });

  // Log both actions
  await logToAudit('CREATE_AGREEMENT', agreement);
  await logToAudit('CREATE_PAYMENT', payment);

  // Commit transaction
  return { agreement, payment };
}
```

### Payment Void on Agreement Termination
```typescript
async function terminateAgreement(agreementId: string, reason: string) {
  // Update agreement status
  await db.agreements.update(agreementId, {
    status: 'terminated',
    terminated_at: new Date()
  });

  // Find linked payment
  const payment = await db.payments.findOne({ agreement_id: agreementId });

  // Auto-void if pending
  if (payment.status === 'pending') {
    await db.payments.update(payment.id, {
      status: 'voided',
      notes: `合約於 ${formatDate(new Date())} 終止 (${reason})`
    });

    await logToAudit('VOID_PAYMENT', {
      payment_id: payment.id,
      reason: 'agreement_terminated'
    });
  }

  // If payment is completed, leave as-is
}
```

### Payment Amount Edit
```typescript
async function editPaymentAmount(
  paymentId: string,
  newAmount: number,
  reason: string
) {
  const payment = await db.payments.findById(paymentId);

  await db.payments.update(paymentId, {
    original_amount: payment.original_amount || payment.amount, // Preserve first original
    amount: newAmount,
    adjustment_reason: reason,
    updated_at: new Date()
  });

  await logToAudit('UPDATE_PAYMENT', {
    payment_id: paymentId,
    old_values: { amount: payment.amount },
    new_values: { amount: newAmount, reason }
  });
}
```

## Source
init_draft.md line 67 (payment tracking), CLAUDE.md (agreement lifecycle)

## Dependencies
- US-AGREE-001 (create agreement - triggers payment creation)
- US-AGREE-006 (terminate agreement - triggers payment void)
- US-SPACE-003 (pricing model - agreement price source)
- US-AUDIT-002 (audit logging)
- US-LOC-003 (TWD currency format)

## Test Data

### Auto-Generated Payment (Normal Flow)
**Agreement Created**:
- Customer: 王小明
- Space: A區-01 (monthly price = NT$4,000)
- Type: Monthly
- Start: 2026-02-01
- Agreement price: NT$4,000

**Payment Auto-Generated**:
- amount: NT$4,000 (from agreement)
- due_date: 2026-02-01
- status: pending
- agreement_id: agr-001

### Payment Amount Edit
**Original Payment**:
- amount: NT$4,000
- status: pending

**Admin Edit**:
- new_amount: NT$3,500
- reason: "VIP客戶折扣 NT$500"

**After Edit**:
- amount: NT$3,500
- original_amount: NT$4,000
- adjustment_reason: "VIP客戶折扣 NT$500"
- Audit log: old_values={amount: 4000}, new_values={amount: 3500}

### Agreement Termination (Auto-Void)
**Before Termination**:
- Agreement: active, start=2026-02-01, end=2026-03-01
- Payment: amount=NT$4,000, status=pending

**Admin Terminates Agreement**:
- reason: "客戶要求提前終止"

**After Termination**:
- Agreement: status=terminated, terminated_at=2026-02-15
- Payment: status=voided, notes="合約於 2026年02月15日 終止 (客戶要求提前終止)"

### Agreement Termination (Payment Already Completed)
**Before Termination**:
- Agreement: active
- Payment: amount=NT$4,000, status=completed, payment_date=2026-02-05

**Admin Terminates Agreement**:
- Agreement → terminated
- Payment → No change (still status=completed) — money already received

### Edge Case: Edit After Void
**Payment**: status=voided (after termination)
- "編輯金額" button hidden (voided payments not editable in Phase 1)
