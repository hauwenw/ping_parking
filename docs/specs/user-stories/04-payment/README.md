# Payment Management Stories

**Total Stories**: 2 (all Must Have)
**Sprint**: Sprint 3 (2 stories)

## Must Have Stories

| ID | Story | Priority | Sprint |
|----|-------|----------|--------|
| US-PAY-001 | Payment Lifecycle (Auto-Generate, Edit, Void) | Must Have | Sprint 3 |
| US-PAY-002 | Record Payment (Manual Completion) | Must Have | Sprint 3 |

**Note**: The payment list view (US-PAY-003) has been merged into US-AGREE-009 (Agreement List View with Payment Status). Since payments are 1:1 with agreements, a separate payment list page is unnecessary — payment status, overdue indicators, and summary cards are displayed on the agreement list page. The US-PAY-003 file is retained for reference but is no longer part of the MVP scope.

## Overview

Manual offline payment tracking for Phase 1. Payments are auto-generated when agreements are created, admin manually records completion when customers pay, and payment history provides visibility into revenue and outstanding amounts.

**Key Dependencies**: Agreement Management (payments linked to agreements), Customer Management (payment tracking), Audit Logging
**Estimated Effort**: 8-10 story points

## Critical Business Rules

### Payment Model
```
payments table:
├── id (UUID, primary key)
├── agreement_id (UUID, foreign key) - 1:1 relationship
├── amount (INTEGER) - Payment amount in NT$ whole dollars
├── original_amount (INTEGER) - Preserved when amount is edited
├── adjustment_reason (TEXT) - Required when amount changed
├── due_date (DATE) - When payment is due (= agreement start_date)
├── payment_date (DATE) - When payment was actually received
├── bank_ref (TEXT) - Bank reference number for reconciliation
├── status (TEXT) - 'pending', 'completed', 'voided'
├── notes (TEXT) - Additional notes
├── created_at (TIMESTAMPTZ)
└── updated_at (TIMESTAMPTZ)
```

### One Payment Per Agreement
- **Auto-generation**: Payment created automatically when agreement is created
- **Amount source**: Payment amount = agreement price (already includes tag pricing effects)
- **No partial payments**: Phase 1 supports one full payment per agreement only
- **1:1 relationship**: Each agreement has exactly one payment record

### Payment Status Lifecycle
```
pending → completed (via US-PAY-002: admin records payment)
       → voided (via US-PAY-001: agreement terminated)
```

**Rules**:
- **pending**: Awaiting customer payment
- **completed**: Payment received and recorded by admin (immutable transition)
- **voided**: Agreement terminated before payment received (auto-void)
- **No reactivation**: Cannot change completed or voided back to pending

### Payment Amount Editing
- Admin can edit payment amount after creation (with required reason)
- Editable for both pending and completed payments
- Original amount preserved in `original_amount` field
- All edits logged to audit trail

### Termination Impact
- **Pending payment + terminated agreement** → Payment auto-voided
- **Completed payment + terminated agreement** → Payment unchanged (money already received)
- Void reason stored in payment notes: "合約於 YYYY-MM-DD 終止 (reason)"

### Overdue Logic
- Payment is **overdue** if: `status='pending' AND current_date > due_date`
- Overdue indicator: Red "⚠️ 逾期 X 天" badge
- Days overdue = `current_date - due_date`

## Relationships

**Payment → Agreement** (1:1):
- One payment per agreement (no partial payments)
- `payments.agreement_id` → `agreements.id`
- Payment due_date = agreement start_date

**Payment → Customer** (indirect via Agreement):
- Payment linked to customer through agreement
- No direct foreign key from payment to customer
- Query: `payments JOIN agreements JOIN customers`

**Payment → Audit Logs** (1:N):
- All payment mutations logged: creation, completion, amount edits, voiding
- Actions: CREATE_PAYMENT, COMPLETE_PAYMENT, UPDATE_PAYMENT, VOID_PAYMENT

## UI Pages

Per `09-ui-ux/README.md`:

1. **付款管理 - 列表** (`/admin/payments`)
   - Table view with summary cards (pending total, completed total, overdue count)
   - Search: customer name, space, bank reference
   - Filters: status, date range, amount range
   - Overdue indicators (red badges)
   - Cross-links to customer and agreement details

2. **付款詳情** (modal or `/admin/payments/:paymentId`)
   - Payment info card (amount, due date, payment date, bank ref, status)
   - Linked agreement and customer info
   - Actions: "記錄付款" (if pending), "編輯金額" (always), "查看合約"

3. **記錄付款 Modal** (triggered from payment detail)
   - Payment date picker (defaults to today)
   - Bank reference input (required)
   - Notes (optional)
   - Validation: date cannot be before agreement start

## Database Schema

```sql
CREATE TABLE payments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agreement_id UUID NOT NULL UNIQUE REFERENCES agreements(id), -- 1:1 relationship
  amount INTEGER NOT NULL CHECK (amount >= 0),
  original_amount INTEGER, -- NULL initially, set when first edited
  adjustment_reason TEXT CHECK (char_length(adjustment_reason) <= 200),
  due_date DATE NOT NULL,
  payment_date DATE, -- NULL until paid
  bank_ref TEXT CHECK (char_length(bank_ref) <= 50 AND bank_ref ~ '^[A-Za-z0-9-]+$'),
  status TEXT NOT NULL CHECK (status IN ('pending', 'completed', 'voided')),
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_payments_agreement_id ON payments(agreement_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_due_date ON payments(due_date);
CREATE INDEX idx_payments_payment_date ON payments(payment_date);
```

## Audit Logging

All payment mutations must log to `system_logs`:
- CREATE payment → `action='CREATE_PAYMENT'`, `old_values=null`, `new_values={amount, due_date, agreement_id}`
- COMPLETE payment → `action='COMPLETE_PAYMENT'`, `old_values={status: 'pending'}`, `new_values={status: 'completed', payment_date, bank_ref}`
- UPDATE amount → `action='UPDATE_PAYMENT'`, `old_values={amount: X}`, `new_values={amount: Y, reason: '...'}`
- VOID payment → `action='VOID_PAYMENT'`, `old_values={status: 'pending'}`, `new_values={status: 'voided', reason: 'agreement_terminated'}`

## Test Data

```json
[
  {
    "id": "pay-001",
    "agreement_id": "agr-001",
    "amount": 4000,
    "due_date": "2026-02-01",
    "payment_date": "2026-02-05",
    "bank_ref": "TXN-20260205-001",
    "status": "completed",
    "notes": "銀行轉帳"
  },
  {
    "id": "pay-002",
    "agreement_id": "agr-002",
    "amount": 3600,
    "due_date": "2026-02-15",
    "payment_date": null,
    "bank_ref": null,
    "status": "pending",
    "notes": null
  },
  {
    "id": "pay-003",
    "agreement_id": "agr-003",
    "amount": 4200,
    "original_amount": 4500,
    "adjustment_reason": "VIP客戶折扣 NT$300",
    "due_date": "2026-01-25",
    "payment_date": null,
    "bank_ref": null,
    "status": "pending",
    "notes": "逾期 21 天 (as of 2026-02-15)"
  },
  {
    "id": "pay-004",
    "agreement_id": "agr-004",
    "amount": 3800,
    "due_date": "2026-02-01",
    "payment_date": null,
    "bank_ref": null,
    "status": "voided",
    "notes": "合約於 2026-02-10 終止 (客戶要求提前終止)"
  }
]
```

## Dependencies

**Referenced by**:
- US-AGREE-001 (Create Agreement) - auto-generates payment
- US-AGREE-006 (Terminate Agreement) - auto-voids pending payment
- US-AGREE-005 (View Agreement Detail) - displays payment status
- US-CUST-002 (Customer Detail) - can view customer's payment history

**References**:
- US-AGREE-001 (agreement must exist to create payment)
- US-CUST-001 (customer linked via agreement)
- US-SPACE-003 (payment amount from agreement price from space price)
- US-LOC-003 (TWD currency format)
- US-LOC-004 (Taiwan date format)
- US-AUDIT-002 (auto-log all actions)

## Future Enhancements (Phase 2/3)

- **Payment gateway integration**: Online payment processing (credit card, bank transfer)
- **Partial payments**: Allow multiple payments per agreement (installments)
- **Payment reminders**: SMS/email notifications for upcoming/overdue payments
- **Batch payment recording**: Record multiple payments at once (CSV import)
- **Payment export**: Export payment history to CSV/Excel
- **Refund processing**: Handle refunds for terminated agreements with completed payments
- **Late fee calculation**: Auto-calculate penalties for overdue payments
- **Receipt generation**: PDF receipts for completed payments
