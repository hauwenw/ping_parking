# US-AGREE-006: Agreement Status (Computed + Manual Termination)

**Priority**: Must Have | **Phase**: Phase 1 | **Sprint**: Sprint 3 (Weeks 5-6)
**Domain**: Agreement Management | **Epic**: Agreement Lifecycle

## User Story
As a parking lot admin, I want agreement status to always reflect reality based on dates, and be able to manually terminate agreements early, so that space availability is always accurate without relying on background jobs.

## Acceptance Criteria
- **AC1**: Agreement status is **computed on-the-fly** from dates and stored termination flag — no cron job required:
  - `status = 'terminated'` → **已終止** (stored, manual action)
  - `current_date < start_date` → **待生效** (computed)
  - `current_date <= end_date` → **進行中** (computed)
  - `current_date > end_date` → **已過期** (computed)
- **AC2**: Space status also computed on-the-fly: "occupied" if any non-terminated agreement has `start_date <= current_date <= end_date`
- **AC3**: Admin clicks "終止合約" on a pending/active agreement → Confirmation dialog: "確定要終止此合約嗎？終止後車位 [name] 將可供重新分配。"
- **AC4**: Termination confirmed → `status` set to `'terminated'`, `terminated_at` timestamp recorded, linked payment auto-voided if pending (see US-PAY-001), logged to system_logs, success message: "合約已終止，車位已釋放"
- **AC5**: Terminated/expired agreement hides "終止合約" button (cannot terminate twice)
- **AC6**: Status badges: 待生效 (pending, blue) / 進行中 (active, green) / 已過期 (expired, gray) / 已終止 (terminated, dark gray)

## Business Rules
- **Computed Status**: pending/active/expired are never stored — always derived from `start_date`, `end_date`, and `current_date`. This eliminates cron job dependency and ensures status is always accurate.
- **Stored Status**: Only `'terminated'` is written to the `status` column. Default value on creation is `'active'` (meaning "not terminated").
- **Manual Termination**: Admin can terminate agreements that are currently pending or active (computed). Cannot terminate already-expired or already-terminated agreements.
- **Space Status**: Computed field — "occupied" only when a non-terminated agreement covers current_date (not stored in DB)
- **Immutable History**: No delete/reactivate of expired/terminated agreements
- **Payment Impact**: Financial history preserved regardless of status
- **Future Enhancement**: Payment status may gate display or alerts (Phase 2)

## UI Requirements
"終止合約" button for pending/active agreements | Confirmation dialog | Success toast | Status badges: 待生效(blue)/進行中(green)/已過期(gray)/已終止(dark gray)

**Badge Color Rationale**:
- **Blue (pending)**: Informational - agreement scheduled to start soon
- **Green (active)**: Current agreements requiring admin attention
- **Gray (expired)**: Neutral historical state - naturally ended (expected lifecycle)
- **Dark Gray (terminated)**: Neutral historical state - manually ended

## Implementation Notes

**Computed Agreement Status** (DB view or application-level helper):
```sql
-- View that computes agreement display status from dates
CREATE OR REPLACE VIEW agreements_with_status AS
SELECT *,
  CASE
    WHEN status = 'terminated' THEN 'terminated'
    WHEN CURRENT_DATE < start_date THEN 'pending'
    WHEN CURRENT_DATE <= end_date THEN 'active'
    ELSE 'expired'
  END AS computed_status
FROM agreements;
```

**Space Status Computation** (computed on-the-fly, not stored):
```sql
-- Space is "occupied" if current_date is within any non-terminated agreement
SELECT spaces.*,
  CASE
    WHEN EXISTS (
      SELECT 1 FROM agreements
      WHERE agreements.space_id = spaces.id
      AND agreements.status != 'terminated'
      AND CURRENT_DATE BETWEEN agreements.start_date AND agreements.end_date
    ) THEN 'occupied'
    ELSE 'available'
  END AS computed_status
FROM spaces;
```

## Source
init_draft.md line 67 (lifecycle) | CLAUDE.md business rules

## Dependencies
US-AGREE-001, US-AGREE-005, US-PAY-001 (payment voiding), US-AUDIT-002

## Test Data

**Computed Pending**: Agreement start_date=2026-03-01, end_date=2026-04-01, today=2026-02-15 → computed_status="pending"

**Computed Active**: Agreement start_date=2026-02-01, end_date=2026-03-01, today=2026-02-15 → computed_status="active"

**Computed Expired**: Agreement start_date=2026-01-01, end_date=2026-01-31, today=2026-02-15 → computed_status="expired"

**Manual Termination**: Agreement start_date=2026-02-01, end_date=2026-03-01, admin terminates on 2026-02-15 → status="terminated", terminated_at=2026-02-15
