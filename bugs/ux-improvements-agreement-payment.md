# UX Improvements: Agreement & Payment Management

**Status**: 📝 Design Phase
**Priority**: Medium
**Estimated Effort**: 8-12 hours
**Implementation Approach**: TDD (Test-Driven Development)

---

## Overview

Three UX improvements to streamline agreement creation and payment management workflows:

1. **Quick Agreement Creation Link** - Add "新增合約" link on every space row for convenient navigation
2. **Smart Price Auto-Population** - Auto-fill price field when space/agreement type selected, with edit capability
3. **Comprehensive Payment Editing** - Full edit modal for updating payment details (amount, status, dates, references)

---

## Feature 1: Quick Agreement Creation Link on Space Page

### Problem
Users must navigate to agreements page separately to create agreements for spaces. No direct shortcut from space list.

### Solution
Add "新增合約" link in the status column of every space row that opens the agreement creation dialog with space pre-selected.

### Technical Design

#### Frontend Changes

**File**: `frontend/src/app/(dashboard)/spaces/page.tsx`

**Location**: Status column (lines 460-473), add link after existing "查看合約" link

**New Code**:
```typescript
<TableCell>
  <div className="flex items-center gap-2">
    <Badge variant={statusColor[s.computed_status || s.status]}>
      {spaceStatusLabel(s.computed_status || s.status)}
    </Badge>
    {s.active_agreement_id && (
      <a href={`/agreements/${s.active_agreement_id}`}
         className="text-xs text-blue-600 hover:underline">
        查看合約
      </a>
    )}
    {/* NEW: Always show create agreement link */}
    <button
      onClick={() => handleCreateAgreementForSpace(s.id)}
      className="text-xs text-green-600 hover:underline"
    >
      新增合約
    </button>
  </div>
</TableCell>
```

**New Handler Function**:
```typescript
const handleCreateAgreementForSpace = (spaceId: string) => {
  // Navigate to agreements page with create dialog open and space pre-selected
  window.location.href = `/agreements?create=true&space_id=${spaceId}`;
};
```

**Alternative Implementation** (if using Next.js router):
```typescript
import { useRouter } from "next/navigation";

const router = useRouter();
const handleCreateAgreementForSpace = (spaceId: string) => {
  router.push(`/agreements?create=true&space_id=${spaceId}`);
};
```

#### Agreements Page Changes

**File**: `frontend/src/app/(dashboard)/agreements/page.tsx`

**New Logic**: Detect URL params to auto-open dialog and pre-select space

**Implementation**:
```typescript
// Add to component state (around line 48)
const [preselectedSpaceId, setPreselectedSpaceId] = useState<string | null>(null);

// Add useEffect to parse URL params
useEffect(() => {
  const params = new URLSearchParams(window.location.search);
  const shouldCreate = params.get("create") === "true";
  const spaceId = params.get("space_id");

  if (shouldCreate && spaceId) {
    setPreselectedSpaceId(spaceId);
    setCreateOpen(true);
    // Clean up URL params
    window.history.replaceState({}, "", "/agreements");
  }
}, []);

// Update space Select to use defaultValue (line 137)
<Select name="space_id" required defaultValue={preselectedSpaceId || undefined}>
  {/* ... existing options ... */}
</Select>
```

### Test Cases (TDD)

**Frontend E2E Tests** (Manual verification):
1. Load `/spaces` page
2. Verify "新增合約" link appears on ALL space rows
3. Click "新增合約" on space "A-01"
4. Should navigate to `/agreements` with create dialog open
5. Space dropdown should have "A-01" pre-selected

**No backend changes needed** - this is purely frontend navigation.

---

## Feature 2: Smart Price Auto-Population on Space Selection

### Problem
Admins must manually enter prices for every agreement. Pricing data already exists in space records but isn't auto-filled.

### Solution
When user selects space + agreement type, automatically populate price field with appropriate value from space pricing. Price remains editable for final adjustments.

### Technical Design

#### Pricing Logic

**Mapping**:
- `agreement_type = "monthly"` → `space.effective_monthly_price`
- `agreement_type = "daily"` → `space.effective_daily_price`
- `agreement_type = "quarterly"` → `space.effective_monthly_price × 3`
- `agreement_type = "yearly"` → `space.effective_monthly_price × 12`

**Edge Cases**:
- If `effective_monthly_price = null` → Leave price field empty (user must enter manually)
- If `effective_daily_price = null` for daily type → Leave empty
- Price field always remains editable after auto-population

#### Frontend Implementation

**File**: `frontend/src/app/(dashboard)/agreements/page.tsx`

**Changes**:

1. **Add state to track selected space and type**:
```typescript
const [selectedSpaceId, setSelectedSpaceId] = useState<string | null>(null);
const [selectedAgreementType, setSelectedAgreementType] = useState<string | null>(null);
```

2. **Add helper function to compute price**:
```typescript
const computePrice = (spaceId: string | null, agreementType: string | null): number | null => {
  if (!spaceId || !agreementType) return null;

  const space = spaces.find(s => s.id === spaceId);
  if (!space) return null;

  switch (agreementType) {
    case "daily":
      return space.effective_daily_price;
    case "monthly":
      return space.effective_monthly_price;
    case "quarterly":
      return space.effective_monthly_price ? space.effective_monthly_price * 3 : null;
    case "yearly":
      return space.effective_monthly_price ? space.effective_monthly_price * 12 : null;
    default:
      return null;
  }
};
```

3. **Update Space Select to track selection** (line 137):
```typescript
<Select
  name="space_id"
  required
  defaultValue={preselectedSpaceId || undefined}
  onValueChange={(value) => setSelectedSpaceId(value)}
>
  {/* ... existing options ... */}
</Select>
```

4. **Update Agreement Type Select to track selection** (line 173):
```typescript
<Select
  name="agreement_type"
  required
  onValueChange={(value) => setSelectedAgreementType(value)}
>
  {/* ... existing options ... */}
</Select>
```

5. **Add useEffect to auto-populate price**:
```typescript
useEffect(() => {
  const price = computePrice(selectedSpaceId, selectedAgreementType);
  if (price !== null) {
    // Find the price input field and set its value
    const priceInput = document.querySelector('input[name="price"]') as HTMLInputElement;
    if (priceInput) {
      priceInput.value = price.toString();
    }
  }
}, [selectedSpaceId, selectedAgreementType, spaces]);
```

**Alternative Controlled Input Approach** (Better):
```typescript
const [priceValue, setPriceValue] = useState<string>("");

useEffect(() => {
  const price = computePrice(selectedSpaceId, selectedAgreementType);
  if (price !== null) {
    setPriceValue(price.toString());
  }
}, [selectedSpaceId, selectedAgreementType, spaces]);

// Update price input (line 189)
<Input
  type="number"
  name="price"
  min={0}
  required
  value={priceValue}
  onChange={(e) => setPriceValue(e.target.value)}
/>
```

### Test Cases (TDD)

**Frontend E2E Tests** (Manual verification):
1. Open create agreement dialog
2. Select space "A-01" (monthly price = 3600)
3. Select agreement type "月租" → Price should show 3600
4. Change type to "季租" → Price should update to 10800 (3600 × 3)
5. Change type to "年租" → Price should update to 43200 (3600 × 12)
6. Manually edit price to 4000 → Should allow override
7. Select space with no pricing → Price field should be empty

**No backend changes needed** - pure frontend calculation.

---

## Feature 3: Comprehensive Payment Editing

### Problem
Current implementation only allows recording payment completion (pending → completed). No way to:
- Edit payment amount after creation
- Change payment status
- Update bank reference or notes after completion
- Set/edit due date

Per US-PAY-001 spec, payments should be editable even after completion.

### Solution
Add "編輯付款" button in agreement detail page that opens edit modal for comprehensive payment updates.

### Technical Design

#### Backend Changes

##### 1. Add `due_date` Field to Payment Model

**File**: `backend/app/models/payment.py`

**Add Column**:
```python
class Payment(UUIDMixin, TimestampMixin, Base):
    # ... existing fields ...
    payment_date: Mapped[date | None]
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)  # NEW
    bank_reference: Mapped[str | None]
    # ... rest of model ...
```

##### 2. Migration Script

**Command**: `alembic revision --autogenerate -m "add due_date to payments"`

**Generated Migration** (verify before running):
```python
def upgrade():
    op.add_column('payments', sa.Column('due_date', sa.Date(), nullable=True))

def downgrade():
    op.drop_column('payments', 'due_date')
```

##### 3. Update Payment Schemas

**File**: `backend/app/schemas/payment.py`

**Add `due_date` to Response**:
```python
class PaymentResponse(BaseModel):
    id: UUID
    agreement_id: UUID
    amount: int
    status: str
    payment_date: date | None
    due_date: date | None  # NEW
    bank_reference: str | None
    notes: str | None

    model_config = {"from_attributes": True}
```

**Create New Update Schema** (comprehensive edit):
```python
class PaymentUpdate(BaseModel):
    """Comprehensive payment update - all fields optional"""
    amount: int | None = Field(None, ge=0)
    status: str | None = Field(None, pattern=r"^(pending|completed|voided)$")
    payment_date: date | None = None
    due_date: date | None = None
    bank_reference: str | None = Field(None, max_length=100)
    notes: str | None = None
```

##### 4. Update Service Layer

**File**: `backend/app/services/payment_service.py`

**Replace `update_amount()` with comprehensive `update()`**:
```python
async def update(self, payment_id: UUID, data: PaymentUpdate) -> Payment:
    """Update payment with any editable fields.

    Allows editing all payments (pending/completed/voided).
    All fields are optional - only provided fields will be updated.
    """
    # Fetch payment
    result = await self.db.execute(
        select(Payment).where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()
    if not payment:
        raise NotFoundError("付款紀錄")

    # Build old_values dict for audit
    old_values = {}

    # Update amount if provided
    if data.amount is not None and data.amount != payment.amount:
        old_values["amount"] = payment.amount
        payment.amount = data.amount

    # Update status if provided
    if data.status is not None and data.status != payment.status:
        old_values["status"] = payment.status
        payment.status = data.status

    # Update payment_date if provided
    if data.payment_date is not None and data.payment_date != payment.payment_date:
        old_values["payment_date"] = payment.payment_date
        payment.payment_date = data.payment_date

    # Update due_date if provided
    if data.due_date is not None and data.due_date != payment.due_date:
        old_values["due_date"] = payment.due_date
        payment.due_date = data.due_date

    # Update bank_reference if provided
    if data.bank_reference is not None and data.bank_reference != payment.bank_reference:
        old_values["bank_reference"] = payment.bank_reference
        payment.bank_reference = data.bank_reference

    # Update notes if provided
    if data.notes is not None and data.notes != payment.notes:
        old_values["notes"] = payment.notes
        payment.notes = data.notes

    # Log update if any changes
    if old_values:
        new_values = {k: getattr(payment, k) for k in old_values.keys()}
        await self.audit.log_update(
            table_name="payments",
            record_id=payment.id,
            old_values=old_values,
            new_values=new_values,
        )

    await self.db.commit()
    await self.db.refresh(payment)
    return payment
```

##### 5. Update API Endpoint

**File**: `backend/app/api/payments.py`

**Replace PUT /amount endpoint**:
```python
@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: UUID,
    data: PaymentUpdate,
    db: DbSession,
    current_user: CurrentUser,
    ip: str = Depends(get_client_ip),
) -> PaymentResponse:
    """Update payment details (amount, status, dates, references).

    Allows editing all payments regardless of status.
    All fields are optional - only provided fields will be updated.
    """
    svc = PaymentService(db, current_user, ip)
    payment = await svc.update(payment_id, data)
    return PaymentResponse.model_validate(payment)
```

##### 6. Update Agreement Creation to Set `due_date`

**File**: `backend/app/services/agreement_service.py`

**Update payment creation** (lines 125-132):
```python
payment = Payment(
    agreement_id=agreement.id,
    amount=data.price,
    status="pending",
    due_date=data.start_date,  # NEW: Default due_date to agreement start_date
)
```

#### Frontend Changes

##### 1. Update Payment Type

**File**: `frontend/src/lib/types.ts`

```typescript
export interface Payment {
  id: string;
  agreement_id: string;
  amount: number;
  status: "pending" | "completed" | "voided";
  payment_date: string | null;
  due_date: string | null;  // NEW
  bank_reference: string | null;
  notes: string | null;
}
```

##### 2. Add Edit Payment Modal

**File**: `frontend/src/app/(dashboard)/agreements/[id]/page.tsx`

**Add state** (around line 40):
```typescript
const [editPaymentOpen, setEditPaymentOpen] = useState(false);
const [editPaymentData, setEditPaymentData] = useState({
  amount: "",
  status: "",
  payment_date: "",
  due_date: "",
  bank_reference: "",
  notes: "",
});
```

**Add handler to open edit modal**:
```typescript
const openEditPayment = () => {
  if (!payment) return;
  setEditPaymentData({
    amount: payment.amount.toString(),
    status: payment.status,
    payment_date: payment.payment_date || "",
    due_date: payment.due_date || agreement.start_date, // Default to start_date
    bank_reference: payment.bank_reference || "",
    notes: payment.notes || "",
  });
  setEditPaymentOpen(true);
};
```

**Add submit handler**:
```typescript
const handleEditPayment = async (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault();
  if (!payment) return;

  const form = new FormData(e.currentTarget);
  const body = {
    amount: Number(form.get("amount")),
    status: form.get("status") as string,
    payment_date: form.get("payment_date") || null,
    due_date: form.get("due_date") || null,
    bank_reference: form.get("bank_reference") || null,
    notes: form.get("notes") || null,
  };

  try {
    await api.put(`/api/v1/payments/${payment.id}`, body);
    toast.success("付款已更新");
    setEditPaymentOpen(false);
    await load();
  } catch (err) {
    if (err instanceof ApiError) toast.error(err.message);
  }
};
```

**Update payment display section** (lines 192-229):
```typescript
<div className="rounded-lg border p-4">
  <div className="flex items-center justify-between mb-4">
    <h3 className="font-semibold">付款資訊</h3>
    <div className="space-x-2">
      {/* Existing "記錄付款" button for pending */}
      {payment.status === "pending" && (
        <Button size="sm" onClick={() => setCompleteOpen(true)}>
          記錄付款
        </Button>
      )}
      {/* NEW: Edit button for all statuses */}
      <Button variant="outline" size="sm" onClick={openEditPayment}>
        編輯付款
      </Button>
    </div>
  </div>

  <div className="space-y-2 text-sm">
    <div className="flex justify-between">
      <span className="text-muted-foreground">狀態</span>
      <Badge variant={paymentStatusColor[payment.status]}>
        {paymentStatusLabel(payment.status)}
      </Badge>
    </div>
    <div className="flex justify-between">
      <span className="text-muted-foreground">金額</span>
      <span className="font-medium">{formatCurrency(payment.amount)}</span>
    </div>
    {/* NEW: Due date display */}
    {payment.due_date && (
      <div className="flex justify-between">
        <span className="text-muted-foreground">應付日期</span>
        <span>{payment.due_date}</span>
      </div>
    )}
    {payment.payment_date && (
      <div className="flex justify-between">
        <span className="text-muted-foreground">付款日期</span>
        <span>{payment.payment_date}</span>
      </div>
    )}
    {/* ... existing bank_reference and notes ... */}
  </div>
</div>
```

**Add Edit Payment Modal** (after complete payment modal):
```tsx
<Dialog open={editPaymentOpen} onOpenChange={setEditPaymentOpen}>
  <DialogContent className="max-w-md">
    <DialogHeader>
      <DialogTitle>編輯付款</DialogTitle>
    </DialogHeader>
    <form onSubmit={handleEditPayment} className="space-y-4">
      <div className="space-y-2">
        <Label>金額 (NT$)</Label>
        <Input
          type="number"
          name="amount"
          min={0}
          required
          defaultValue={editPaymentData.amount}
        />
      </div>

      <div className="space-y-2">
        <Label>狀態</Label>
        <Select name="status" required defaultValue={editPaymentData.status}>
          <SelectTrigger><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="pending">待付款</SelectItem>
            <SelectItem value="completed">已付款</SelectItem>
            <SelectItem value="voided">已作廢</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label>應付日期</Label>
        <Input
          type="date"
          name="due_date"
          defaultValue={editPaymentData.due_date}
        />
        <p className="text-xs text-muted-foreground">
          預設為合約開始日期，可手動調整
        </p>
      </div>

      <div className="space-y-2">
        <Label>付款日期</Label>
        <Input
          type="date"
          name="payment_date"
          defaultValue={editPaymentData.payment_date}
        />
      </div>

      <div className="space-y-2">
        <Label>銀行參考號</Label>
        <Input
          name="bank_reference"
          maxLength={100}
          defaultValue={editPaymentData.bank_reference}
          placeholder="轉帳單號或參考號碼"
        />
      </div>

      <div className="space-y-2">
        <Label>備註</Label>
        <Textarea
          name="notes"
          rows={3}
          defaultValue={editPaymentData.notes}
          placeholder="付款備註（選填）"
        />
      </div>

      <DialogFooter>
        <Button type="button" variant="outline" onClick={() => setEditPaymentOpen(false)}>
          取消
        </Button>
        <Button type="submit">儲存</Button>
      </DialogFooter>
    </form>
  </DialogContent>
</Dialog>
```

### Test Cases (TDD)

#### Backend Tests

**File**: `backend/tests/test_payments.py`

**New Tests**:

1. **`test_update_payment_amount`**
   - Create agreement with payment (amount=3600)
   - Call `PUT /api/v1/payments/{id}` with `{"amount": 3000}`
   - Assert payment.amount = 3000
   - Assert audit log exists with old_values={amount: 3600}, new_values={amount: 3000}

2. **`test_update_payment_status`**
   - Create payment with status="pending"
   - Update to status="completed"
   - Assert status changed
   - Assert audit logged

3. **`test_update_payment_due_date`**
   - Create payment
   - Update due_date to 7 days after start_date
   - Assert due_date changed
   - Assert audit logged

4. **`test_update_completed_payment_allowed`**
   - Create payment, complete it (status="completed")
   - Update amount from 3600 to 3000
   - **Should succeed** (spec allows editing completed payments)
   - Assert amount changed

5. **`test_update_multiple_fields`**
   - Update amount, status, bank_reference in single request
   - Assert all fields updated
   - Assert audit log contains all changes

6. **`test_payment_auto_generation_with_due_date`**
   - Create agreement with start_date = 2026-03-01
   - Assert payment.due_date = 2026-03-01 (defaults to start_date)

**Update Existing Test**:

7. **`test_payment_amount_update_only_pending`** (line 95-109)
   - **DELETE THIS TEST** - outdated restriction
   - Replace with `test_update_completed_payment_allowed`

#### Frontend Tests

**Manual E2E Verification**:

1. Navigate to agreement detail page
2. Verify "編輯付款" button appears
3. Click button → Edit modal opens with all fields pre-filled
4. Edit amount from 3600 to 3000
5. Change status from pending to completed
6. Add bank reference
7. Submit → Should see success toast
8. Refresh page → Changes persisted
9. Check system logs → UPDATE action logged

---

## Database Schema Changes

### Migration Summary

**Table**: `payments`

**Add Column**:
- `due_date` (DATE, nullable) - Default to agreement.start_date, editable by admin

**No changes to**:
- Foreign keys
- Indexes
- Constraints

### Migration Command

```bash
cd backend
alembic revision --autogenerate -m "add due_date to payments table"
alembic upgrade head
```

---

## API Changes Summary

### New Endpoints

None (replacing existing endpoint)

### Modified Endpoints

**PUT `/api/v1/payments/{payment_id}`** (previously `/api/v1/payments/{payment_id}/amount`)

**Old Behavior**:
- Only updates `amount` field
- Only works for `status='pending'`
- Requires `notes` field (reason)

**New Behavior**:
- Updates any combination of: amount, status, payment_date, due_date, bank_reference, notes
- Works for all payment statuses (pending/completed/voided)
- All fields optional

**Request Schema**:
```json
{
  "amount": 3000,
  "status": "completed",
  "payment_date": "2026-03-15",
  "due_date": "2026-03-01",
  "bank_reference": "BANK-12345",
  "notes": "Discounted payment"
}
```

**Response**: `PaymentResponse` with updated fields

---

## Implementation Phases (TDD Approach)

### Phase 1: Feature 3 Backend (Payment Editing) - ~3 hours

**TDD Cycle**:
1. **RED**: Write failing test `test_update_payment_amount`
2. **GREEN**: Add `due_date` field to model + migration
3. **GREEN**: Update schemas (PaymentUpdate, PaymentResponse)
4. **GREEN**: Implement `PaymentService.update()` method
5. **GREEN**: Update API endpoint
6. **REFACTOR**: Test passes, clean up code
7. **REPEAT**: For tests 2-6

**Deliverables**:
- Migration script
- Updated Payment model
- Updated schemas
- Updated service layer
- Updated API endpoint
- 6 passing backend tests

### Phase 2: Feature 2 Frontend (Price Auto-Population) - ~2 hours

**TDD Cycle**:
1. **Implementation**: Add state tracking for selectedSpaceId, selectedAgreementType
2. **Implementation**: Add computePrice() helper
3. **Implementation**: Add onValueChange handlers to Select components
4. **Implementation**: Add useEffect to auto-populate price
5. **Manual Testing**: Verify all test cases

**Deliverables**:
- Updated agreement create form
- Working price auto-population
- Verified edge cases (no price, quarterly/yearly calculation)

### Phase 3: Feature 1 Frontend (Agreement Link) - ~1 hour

**Implementation**:
1. Add "新增合約" button to space page status column
2. Add handleCreateAgreementForSpace handler
3. Update agreements page to parse URL params
4. Add useEffect to auto-open dialog and pre-select space

**Deliverables**:
- "新增合約" link on all space rows
- Working navigation with pre-selection

### Phase 4: Feature 3 Frontend (Payment Edit UI) - ~3 hours

**Implementation**:
1. Update Payment type with due_date field
2. Add edit payment modal component
3. Add edit button to payment info section
4. Add handlers for opening modal and submitting edits
5. Update payment display to show due_date

**Deliverables**:
- Working edit payment modal
- Updated payment display
- Manual E2E verification

### Phase 5: Integration Testing - ~1 hour

**Full Workflow Tests**:
1. Create space with pricing
2. Click "新增合約" from space page
3. Verify space pre-selected
4. Verify price auto-populated
5. Create agreement
6. Edit payment via new modal
7. Verify all changes persisted

---

## Risk Assessment

### Low Risk
- **Feature 1**: Pure frontend navigation, no data changes
- **Feature 2**: Pure frontend calculation, no backend changes

### Medium Risk
- **Feature 3 Backend**: Adding nullable column is safe (no data migration needed)
- **Feature 3 Frontend**: Comprehensive edit form requires careful validation

### Mitigation
- Use TDD to catch issues early
- Test with existing production-like data
- Add audit logging for all payment updates (already implemented)
- Make `due_date` nullable to avoid breaking existing records

---

## Rollback Plan

If issues arise:

1. **Feature 1**: Remove "新增合約" link, revert agreements page URL parsing
2. **Feature 2**: Remove onValueChange handlers, remove computePrice logic
3. **Feature 3**:
   - Backend: Run migration downgrade to remove `due_date` column
   - Frontend: Remove edit payment modal and button
   - Restore old PUT /amount endpoint if needed

---

## Documentation Updates

After implementation:

1. Update `docs/specs/user-stories/04-payment/US-PAY-001-payment-lifecycle.md`
   - Mark AC10 as ✅ Implemented (edit completed payments)
   - Document `due_date` field
   - Update test cases

2. Update `docs/specs/user-stories/03-agreement/README.md`
   - Document quick agreement creation link
   - Document price auto-population UX

3. Update `CLAUDE.md`
   - Add payment editing capability to Payment Lifecycle section
   - Document `due_date` field in payment model

---

## Success Criteria

- ✅ "新增合約" link appears on all space rows
- ✅ Clicking link navigates to agreements page with dialog open and space pre-selected
- ✅ Selecting space + agreement type auto-populates price field
- ✅ Price calculation correct for all types (monthly, daily, quarterly=×3, yearly=×12)
- ✅ Price field remains editable after auto-population
- ✅ "編輯付款" button appears on agreement detail page
- ✅ Edit modal allows updating amount, status, dates, bank reference, notes
- ✅ Editing completed payments works (no restriction)
- ✅ `due_date` defaults to agreement start_date on creation
- ✅ `due_date` is editable in payment edit modal
- ✅ All payment updates logged to system_logs
- ✅ All 6 backend tests passing
- ✅ Manual E2E verification passes

---

## Timeline Estimate

- **Phase 1** (Payment Backend): 3 hours
- **Phase 2** (Price Auto-fill): 2 hours
- **Phase 3** (Agreement Link): 1 hour
- **Phase 4** (Payment Edit UI): 3 hours
- **Phase 5** (Integration Testing): 1 hour

**Total**: 10 hours (within 8-12 hour estimate)

---

**Next Steps**: Get user approval on this design plan, then proceed to Phase 1 implementation using TDD.
