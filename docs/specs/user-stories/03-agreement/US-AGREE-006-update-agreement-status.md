# US-AGREE-006: Update Agreement Status (Active/Expired/Terminated)

**Priority**: Must Have | **Phase**: Phase 1 | **Sprint**: Sprint 3 (Weeks 5-6)
**Domain**: Agreement Management | **Epic**: Agreement Lifecycle

## User Story
As a parking lot admin, I want agreements to automatically activate on their start date and expire on their end date, with the ability to manually terminate early, so that space availability reflects current reality without manual intervention.

## Acceptance Criteria
- **AC1**: Daily batch job (midnight Taiwan time) handles automatic status transitions:
  - `pending` agreements: current_date >= start_date → status="active"
  - `active` agreements: current_date > end_date → status="expired"
- **AC2**: Agreement activates → Space computed status updates to "occupied" (if current_date within active agreement range), logged to system_logs
- **AC3**: Agreement expires → Space computed status updates to "available" (if no other active agreements), logged to system_logs with action="AUTO_EXPIRE"
- **AC4**: Admin clicks "終止合約" on pending/active agreement → Confirmation dialog: "確定要終止此合約嗎？終止後車位 [name] 將可供重新分配。"
- **AC5**: Termination confirmed → status="terminated", space becomes available for that date range, reason stored ("管理員手動終止"), logged, success message: "合約已終止，車位已釋放"
- **AC6**: Terminated/expired agreement hides "終止合約" button (cannot terminate twice)
- **AC7**: Status lifecycle: `pending` → `active` → `expired`/`terminated` (no reactivation, no status reversal)
- **AC8**: Status badges: 待生效 (pending, blue) / 進行中 (active, green) / 已過期 (expired, gray) / 已終止 (terminated, dark gray)

## Business Rules
- **Automatic Activation**: `pending` → `active` when start_date arrives (no payment status check in Phase 1)
- **Automatic Expiration**: `active` → `expired` when end_date passes
- **Manual Termination**: Admin can end `pending` or `active` agreements early
- **Space Status**: Computed field based on current_date and active agreements (not stored in DB)
- **Immutable History**: No delete/reactivate of expired/terminated agreements
- **Payment Impact**: Financial history preserved regardless of status
- **Future Enhancement**: Payment status will gate auto-activation (Phase 2 - unpaid agreements won't activate)

## UI Requirements
"終止合約" button for pending/active agreements | Confirmation dialog | Success toast | Status badges: 待生效(blue)/進行中(green)/已過期(gray)/已終止(dark gray)

**Badge Color Rationale**:
- **Blue (pending)**: Informational - agreement scheduled to start soon
- **Green (active)**: Current agreements requiring admin attention
- **Gray (expired)**: Neutral historical state - naturally ended (expected lifecycle)
- **Dark Gray (terminated)**: Neutral historical state - manually ended

## Implementation Notes

**Cron Job** (runs daily at midnight Taiwan time - UTC+8):
```typescript
// Vercel Cron or Supabase Edge Function
export async function updateAgreementStatuses() {
  const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD

  // Activate pending agreements
  await supabase
    .from('agreements')
    .update({ status: 'active', updated_at: new Date() })
    .eq('status', 'pending')
    .lte('start_date', today);

  // Expire active agreements
  await supabase
    .from('agreements')
    .update({ status: 'expired', updated_at: new Date() })
    .eq('status', 'active')
    .lt('end_date', today);

  // Log to system_logs (action="AUTO_ACTIVATE" / "AUTO_EXPIRE")
}
```

**Space Status Computation** (computed on-the-fly, not stored):
```sql
-- Space is "occupied" if current_date is within any active agreement
SELECT spaces.*,
  CASE
    WHEN EXISTS (
      SELECT 1 FROM agreements
      WHERE agreements.space_id = spaces.id
      AND agreements.status = 'active'
      AND CURRENT_DATE BETWEEN agreements.start_date AND agreements.end_date
    ) THEN 'occupied'
    ELSE 'available'
  END AS computed_status
FROM spaces;
```

## Source
init_draft.md line 67 (lifecycle) | CLAUDE.md business rules

## Dependencies
US-AGREE-001, US-AGREE-005, US-AUDIT-002

## Test Data
Agreement 1: Active, end_date=2026-01-31, today=2026-02-01 → Auto-expire | Agreement 2: Active, admin terminates → status="terminated"
