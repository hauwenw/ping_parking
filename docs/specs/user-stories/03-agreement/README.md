# Agreement Management Stories

**Total Stories**: 9 (all Must Have)
**Sprint**: Sprint 3 (6 stories) + Sprint 4 (3 stories)

## Must Have Stories

| ID | Story | Priority | Sprint |
|----|-------|----------|--------|
| US-AGREE-001 | Create Monthly Rental Agreement | Must Have | Sprint 3 |
| US-AGREE-002 | Auto-Calculate Agreement End Dates | Must Have | Sprint 3 |
| US-AGREE-003 | Require License Plate for All Types | Must Have | Sprint 3 |
| US-AGREE-004 | Prevent Double-Booking | Must Have | Sprint 3 |
| US-AGREE-005 | View Agreement Details | Must Have | Sprint 3 |
| US-AGREE-006 | Agreement Status (Computed + Termination) | Must Have | Sprint 3 |
| US-AGREE-007 | Create Daily/Quarterly/Yearly Agreements | Must Have | Sprint 4 |
| US-AGREE-008 | Cross-Page Navigation | Must Have | Sprint 4 |
| US-AGREE-009 | Agreement List View (with Payment Status) | Must Have | Sprint 4 |

## Overview

Complete rental contract lifecycle: create agreements (daily/monthly/quarterly/yearly), auto-calculate end dates, enforce business rules (one space = one active agreement), license plate tracking, status management, and cross-page navigation.

**Key Dependencies**: Customer, Space, Payment domains, Localization, Audit
**Estimated Effort**: 20-24 story points (most complex domain)

**Critical Business Rules**:
- **Date Range Validation**: Space can have multiple agreements if date ranges don't overlap (not just "one active")
- **License Plates**: At least one required, multiple allowed for ALL agreement types (stored as TEXT[] array - see US-AGREE-003)
- **End Dates**: Auto-calculated based on type (daily: +1d, monthly: +1mo, quarterly: +3mo, yearly: +1yr). See US-AGREE-002
- **Custom End Dates**: Phase 1 auto-calculates only. Future enhancement (Phase 2/3) will allow manual override for special cases
- **Agreement Lifecycle**: pending → active → expired (computed from dates, no cron job — see US-AGREE-006) / terminated (manual)
- **Space Status**: Computed field (occupied = has active agreement RIGHT NOW), NOT a stored "reserved" status
- **Payment**: Auto-generated at agreement creation (not activation) with due_date=start_date

## Agreement Data Model

```
agreements table:
├── id (UUID, primary key)
├── customer_id (UUID, FK → customers) - Who is renting
├── space_id (UUID, FK → spaces) - Which space
├── agreement_type (TEXT) - 'daily', 'monthly', 'quarterly', 'yearly'
├── license_plates (TEXT[], min 1) - At least one plate required
├── start_date (DATE) - Rental start
├── end_date (DATE) - Auto-calculated, exclusive (space free on this date)
├── price (INTEGER) - NT$ whole dollars, snapshot at creation time
├── terminated_at (TIMESTAMPTZ, nullable) - Only stored status
├── termination_reason (TEXT, max 200 chars) - Required when terminated
├── notes (TEXT, max 500 chars, optional)
├── created_at (TIMESTAMPTZ)
└── updated_at (TIMESTAMPTZ)
```

### Computed Status (via View)

Status is **never stored as a column** — derived from dates and termination:

| Status | Condition | Stored? |
|--------|-----------|---------|
| `terminated` | `terminated_at IS NOT NULL` | Yes (only this one) |
| `pending` | `today < start_date` | No, computed |
| `active` | `start_date <= today < end_date` | No, computed |
| `expired` | `today >= end_date` | No, computed |

Priority: `terminated` checked first (overrides date-based status).

### Editability Rules (Phase 1)

Most agreement fields are **immutable after creation** — if wrong, terminate and recreate. Two fields are always editable regardless of status:

| Field | Editable? | Reason |
|-------|-----------|--------|
| `notes` | Always | Manager needs to jot down context anytime |
| `license_plates` | Always | Plates may change mid-agreement |
| `price` | Never | Snapshot at creation, affects payment |
| `start_date` / `end_date` | Never | Affects status computation |
| `agreement_type` | Never | Determines end date |
| `customer_id` / `space_id` | Never | Core relationship |

Edits to `notes` and `license_plates` are logged to `system_logs` with old/new values.

## Database Schema

```sql
CREATE TABLE agreements (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Relationships
  customer_id UUID NOT NULL REFERENCES customers(id),
  space_id UUID NOT NULL REFERENCES spaces(id),

  -- Agreement details
  agreement_type TEXT NOT NULL CHECK (agreement_type IN ('daily', 'monthly', 'quarterly', 'yearly')),
  license_plates TEXT[] NOT NULL CHECK (array_length(license_plates, 1) >= 1),
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  price INTEGER NOT NULL CHECK (price >= 0),  -- NT$ whole dollars, snapshot at creation

  -- Termination (only stored status; active/pending/expired are computed)
  terminated_at TIMESTAMPTZ,
  termination_reason TEXT CHECK (char_length(termination_reason) <= 200),

  -- Metadata
  notes TEXT CHECK (char_length(notes) <= 500),
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),

  -- Constraints
  CONSTRAINT chk_dates CHECK (end_date > start_date)
);

-- Indexes
CREATE INDEX idx_agreements_customer_id ON agreements(customer_id);
CREATE INDEX idx_agreements_space_id ON agreements(space_id);
CREATE INDEX idx_agreements_start_date ON agreements(start_date);
CREATE INDEX idx_agreements_end_date ON agreements(end_date);
CREATE INDEX idx_agreements_type ON agreements(agreement_type);
```

### Computed Status View (US-AGREE-006)

```sql
CREATE OR REPLACE VIEW agreements_with_status AS
SELECT *,
  CASE
    WHEN terminated_at IS NOT NULL THEN 'terminated'
    WHEN current_date < start_date THEN 'pending'
    WHEN current_date >= start_date AND current_date < end_date THEN 'active'
    ELSE 'expired'
  END AS status
FROM agreements;
```

### Double-Booking Prevention Trigger (US-AGREE-004)

Prevents two non-terminated agreements on the same space with overlapping dates:

```sql
CREATE OR REPLACE FUNCTION check_space_overlap()
RETURNS TRIGGER AS $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM agreements
    WHERE space_id = NEW.space_id
      AND id != COALESCE(NEW.id, '00000000-0000-0000-0000-000000000000'::uuid)
      AND terminated_at IS NULL
      AND start_date < NEW.end_date
      AND end_date > NEW.start_date
  ) THEN
    RAISE EXCEPTION '此車位在該期間已有有效合約';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_space_overlap
  BEFORE INSERT ON agreements
  FOR EACH ROW EXECUTE FUNCTION check_space_overlap();
```

### Auto-Calculate End Date (US-AGREE-002)

```sql
CREATE OR REPLACE FUNCTION calculate_end_date(p_start DATE, p_type TEXT)
RETURNS DATE AS $$
BEGIN
  RETURN CASE p_type
    WHEN 'daily'     THEN p_start + INTERVAL '1 day'
    WHEN 'monthly'   THEN p_start + INTERVAL '1 month'
    WHEN 'quarterly' THEN p_start + INTERVAL '3 months'
    WHEN 'yearly'    THEN p_start + INTERVAL '1 year'
  END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;
```

## Relationships

**Agreement → Customer** (N:1):
- `agreements.customer_id` → `customers.id`
- One customer can have multiple agreements (historical + active)

**Agreement → Space** (N:1):
- `agreements.space_id` → `spaces.id`
- One space can have multiple agreements, but only one non-terminated with overlapping dates

**Agreement → Payment** (1:1):
- `payments.agreement_id` → `agreements.id` (FK lives on payments side)
- Auto-generated at agreement creation

**Agreement → Audit Logs** (1:N):
- All mutations logged: creation, termination

## Audit Logging

All agreement mutations must log to `system_logs`:
- CREATE agreement → `action='CREATE'`, `new_values={customer_id, space_id, type, plates, dates, price}`
- UPDATE agreement (notes/plates) → `action='UPDATE'`, `old_values={notes: "old"}`, `new_values={notes: "new"}`
- TERMINATE agreement → `action='TERMINATE'`, `old_values={status: 'active'}`, `new_values={terminated_at, reason}`

## Test Data

```json
[
  {
    "id": "agr-001",
    "customer_id": "cust-001",
    "space_id": "space-A-01",
    "agreement_type": "monthly",
    "license_plates": ["ABC-1234"],
    "start_date": "2026-02-01",
    "end_date": "2026-03-01",
    "price": 4000,
    "terminated_at": null,
    "notes": null,
    "computed_status": "active"
  },
  {
    "id": "agr-002",
    "customer_id": "cust-002",
    "space_id": "space-B-05",
    "agreement_type": "quarterly",
    "license_plates": ["XYZ-5678", "DEF-9012"],
    "start_date": "2026-03-01",
    "end_date": "2026-06-01",
    "price": 10800,
    "terminated_at": null,
    "notes": "VIP客戶，兩台車共用車位",
    "computed_status": "pending"
  },
  {
    "id": "agr-003",
    "customer_id": "cust-003",
    "space_id": "space-A-12",
    "agreement_type": "monthly",
    "license_plates": ["GHI-3456"],
    "start_date": "2026-01-01",
    "end_date": "2026-02-01",
    "price": 3600,
    "terminated_at": null,
    "notes": null,
    "computed_status": "expired"
  },
  {
    "id": "agr-004",
    "customer_id": "cust-001",
    "space_id": "space-C-03",
    "agreement_type": "daily",
    "license_plates": ["ABC-1234"],
    "start_date": "2026-02-10",
    "end_date": "2026-02-11",
    "price": 150,
    "terminated_at": "2026-02-10T14:30:00+08:00",
    "termination_reason": "客戶要求提前終止",
    "notes": null,
    "computed_status": "terminated"
  }
]
```

## Dependencies

**Referenced by**:
- US-PAY-001 (Payment Lifecycle) - auto-generates payment on creation
- US-PAY-002 (Record Payment) - payment linked to agreement
- US-CUST-002 (Customer Detail) - displays customer's agreements
- US-CUST-005 (Link to Agreement) - cross-navigation

**References**:
- US-CUST-001 (customer must exist)
- US-SPACE-002 (space must exist)
- US-SPACE-003 (price from space pricing hierarchy)
- US-LOC-003 (TWD currency format)
- US-LOC-004 (Taiwan date format)
- US-AUDIT-002 (auto-log all actions)

## Future Enhancements (Phase 2/3)

- **Edit agreement**: Allow editing more fields (e.g., dates, price with approval)
- **Custom end dates**: Manual override for non-standard agreements
- **Renewal chain**: Link renewed agreements to originals
- **Bulk agreement creation**: CSV import (US-BULK-003)
- **Agreement export**: Export filtered list to CSV/Excel
- **Partial payments**: Multiple payments per agreement (installments)
