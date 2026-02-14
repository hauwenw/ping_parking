# System Audit Stories

**Total Stories**: 3 (all Must Have)
**Sprint**: Sprint 1 (2 stories) + Sprint 4 (1 story)

## Stories

| ID | Story | Priority | Sprint |
|----|-------|----------|--------|
| US-AUDIT-001 | View System Audit Log | Must Have | Sprint 1 |
| US-AUDIT-002 | Auto-Log All Admin Actions | Must Have | Sprint 1 |
| US-AUDIT-003 | Export Audit Log to CSV | Must Have | Sprint 4 |

## Overview

Complete audit trail: automatic logging of all admin actions, searchable audit log view, and CSV export for compliance.

**Key Dependencies**: FastAPI AuditLogger service, system_logs table
**Estimated Effort**: 8-10 story points

**Implementation Order**: US-AUDIT-002 first (foundation), then US-AUDIT-001 (view), finally US-AUDIT-003 (export)

## System Logs Data Model

```
system_logs table:
├── id (UUID, primary key)
├── user_id (UUID, FK → admin_users, nullable) - Admin who performed the action
├── action (TEXT) - CREATE, UPDATE, DELETE, CSV_IMPORT, LOGIN, LOGOUT, FAILED_LOGIN, TERMINATE
├── table_name (TEXT) - Target table: customers, spaces, agreements, payments, tags, sites
├── record_id (UUID, nullable) - Target record (null for batch/auth actions)
├── old_values (JSONB, nullable) - Previous state (UPDATE, DELETE, TERMINATE)
├── new_values (JSONB, nullable) - New state (CREATE, UPDATE, CSV_IMPORT)
├── ip_address (INET, nullable) - Client IP address
├── batch_id (UUID, nullable) - Groups CSV import entries together
├── metadata (JSONB, nullable) - Extra context (e.g., CSV totals, termination reason)
├── created_at (TIMESTAMPTZ) - Immutable timestamp
└── (no updated_at — logs are immutable)
```

## Database Schema

```sql
CREATE TABLE system_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Who
  user_id UUID REFERENCES admin_users(id),

  -- What
  action TEXT NOT NULL CHECK (action IN (
    'CREATE', 'UPDATE', 'DELETE',
    'CSV_IMPORT',
    'LOGIN', 'LOGOUT', 'FAILED_LOGIN',
    'TERMINATE'
  )),
  table_name TEXT CHECK (table_name IN (
    'customers', 'spaces', 'agreements', 'payments',
    'tags', 'sites', 'waiting_list'
  )),
  record_id UUID,

  -- Change data
  old_values JSONB,
  new_values JSONB,

  -- Context
  ip_address INET,
  batch_id UUID,        -- groups CSV import rows
  metadata JSONB,       -- extra context (e.g., {total: 50, success: 48, failed: 2})

  -- Timestamp (immutable, no updated_at)
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes for common query patterns (US-AUDIT-001 filters)
CREATE INDEX idx_system_logs_created_at ON system_logs(created_at DESC);
CREATE INDEX idx_system_logs_user_id ON system_logs(user_id);
CREATE INDEX idx_system_logs_action ON system_logs(action);
CREATE INDEX idx_system_logs_table_name ON system_logs(table_name);
CREATE INDEX idx_system_logs_record_id ON system_logs(record_id);
CREATE INDEX idx_system_logs_batch_id ON system_logs(batch_id) WHERE batch_id IS NOT NULL;

-- Composite index for common filtered queries (date + table)
CREATE INDEX idx_system_logs_table_date ON system_logs(table_name, created_at DESC);
```

### Immutability Enforcement

Logs cannot be updated or deleted. Enforced via database trigger + application-layer middleware:

```sql
-- Trigger: block UPDATE and DELETE on system_logs
CREATE OR REPLACE FUNCTION prevent_log_mutation()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION '系統日誌不可修改或刪除';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_prevent_log_mutation
  BEFORE UPDATE OR DELETE ON system_logs
  FOR EACH ROW EXECUTE FUNCTION prevent_log_mutation();
```

### Access Control

RLS dropped (US-SEC-005) — access control handled in FastAPI auth middleware. Single DB user connects directly; all log reads/writes go through the AuditLogger service which enforces immutability at the application layer. The database trigger above provides an additional safety net.

## Action Types Reference

| Action | Table | old_values | new_values | Notes |
|--------|-------|------------|------------|-------|
| `CREATE` | any | null | `{name, phone, ...}` | New record created |
| `UPDATE` | any | `{phone: "old"}` | `{phone: "new"}` | Only changed fields |
| `DELETE` | any | `{full record}` | null | Full record snapshot |
| `TERMINATE` | agreements | `{status: "active"}` | `{terminated_at, reason}` | Agreement-specific |
| `CSV_IMPORT` | any | null | `{batch_id}` | Per-record + batch summary |
| `LOGIN` | null | null | null | metadata: `{method}` |
| `LOGOUT` | null | null | null | — |
| `FAILED_LOGIN` | null | null | null | metadata: `{reason}` |

## Design Decisions

1. **No `updated_at`** — Logs are immutable. No updates ever.
2. **`table_name` not `table`** — Avoids PostgreSQL reserved word.
3. **`INET` for IP** — Native PostgreSQL type, supports IPv4/IPv6, enables range queries.
4. **`batch_id`** — Groups CSV import rows so the audit view can show "50 customers imported" as one logical action while keeping per-record traceability.
5. **`metadata` JSONB** — Extensible context without schema changes. Used for CSV totals, login methods, etc.
6. **Server-side insert only** — Client-side code cannot write logs directly. Logs are created via FastAPI AuditLogger service.
7. **Separate `TERMINATE` action** — Distinguished from generic `UPDATE` for clarity in audit log filtering.

## Performance Notes (Issue #8)

- **Partitioning**: If logs exceed ~10M rows, consider range-partitioning by `created_at` (monthly).
- **Retention**: All logs retained indefinitely (min 3 years per business requirement).
- **Latency target**: <50ms overhead per operation (US-AUDIT-002 AC7).
- **Non-blocking**: Log failures must NOT block the primary operation (US-AUDIT-002 AC8).

## Test Data

```json
[
  {
    "id": "log-001",
    "user_id": "admin-001",
    "action": "CREATE",
    "table_name": "customers",
    "record_id": "cust-001",
    "old_values": null,
    "new_values": {"name": "王大明", "phone": "0912345678"},
    "ip_address": "192.168.1.100",
    "batch_id": null,
    "metadata": null,
    "created_at": "2026-02-01T09:30:00+08:00"
  },
  {
    "id": "log-002",
    "user_id": "admin-001",
    "action": "UPDATE",
    "table_name": "customers",
    "record_id": "cust-001",
    "old_values": {"phone": "0912345678"},
    "new_values": {"phone": "0912999888"},
    "ip_address": "192.168.1.100",
    "batch_id": null,
    "metadata": null,
    "created_at": "2026-02-01T10:15:00+08:00"
  },
  {
    "id": "log-003",
    "user_id": "admin-001",
    "action": "CSV_IMPORT",
    "table_name": "customers",
    "record_id": null,
    "old_values": null,
    "new_values": null,
    "ip_address": "192.168.1.100",
    "batch_id": "batch-001",
    "metadata": {"total": 50, "success": 48, "failed": 2},
    "created_at": "2026-02-02T14:00:00+08:00"
  },
  {
    "id": "log-004",
    "user_id": "admin-001",
    "action": "TERMINATE",
    "table_name": "agreements",
    "record_id": "agr-004",
    "old_values": {"status": "active"},
    "new_values": {"terminated_at": "2026-02-10T14:30:00+08:00", "reason": "客戶要求提前終止"},
    "ip_address": "192.168.1.100",
    "batch_id": null,
    "metadata": null,
    "created_at": "2026-02-10T14:30:00+08:00"
  }
]
```

## Dependencies

**Referenced by**: Every domain that performs CRUD operations
**References**:
- `admin_users` table for `user_id`
- US-SEC-001 (admin authentication provides user_id)
