# US-AUDIT-002: Auto-Log All Admin Actions to System Audit Trail

**Priority**: Must Have
**Phase**: Phase 1
**Domain**: System Audit
**Epic**: Audit Logging & Compliance
**Sprint**: Sprint 1 (Weeks 1-2)

## User Story

As a system administrator,
I want all admin create/update/delete actions automatically logged to system_logs table,
So that we have a complete, immutable audit trail without relying on manual logging.

## Acceptance Criteria

- **AC1**: Every create/update/delete on customers, spaces, agreements, payments, tags, waiting_list, sites triggers audit log
- **AC2**: Each log entry includes: action, user_id, table, record_id, old_values, new_values, timestamp, ip_address
- **AC3**: CSV import logs with: action=CSV_IMPORT, batch_id, total/successful/failed records count
- **AC4**: Authentication events log: LOGIN, LOGOUT, FAILED_LOGIN
- **AC5**: Logging happens AFTER successful transaction (not before)
- **AC6**: Failed actions do NOT generate logs (only successful changes)
- **AC7**: Performance: Audit logging adds <50ms latency
- **AC8**: Log failures do NOT block primary operation

## Business Rules

- Immutability: Logs cannot be updated/deleted (trigger + RLS enforced)
- Async Logging: Avoid blocking user operations
- Server-Side Only: Database triggers or API middleware (not client)
- Sensitive Data: Do NOT log passwords, JWT tokens
- Complete Capture: Log both old and new values for UPDATE

## Verification Method

- Create customer → Verify log with action=CREATE, new_values populated
- Update customer → Verify log shows old vs new values
- Delete space → Verify log with action=DELETE, old_values populated
- CSV import 50 customers → Verify batch log
- Performance test: 100 rapid creates, verify <50ms latency per operation

## Source

- init_draft.md lines 30, 70, 128
- CLAUDE.md system logging

## Dependencies

- All CRUD operations

## Related Stories

- US-AUDIT-001 (view logs)
- US-SEC-005 (RLS on system_logs)
- US-BULK-001 through US-BULK-006 (CSV logging)
