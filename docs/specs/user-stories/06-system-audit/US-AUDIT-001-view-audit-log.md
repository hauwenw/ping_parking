# US-AUDIT-001: View System Audit Log

**Priority**: Must Have
**Phase**: Phase 1
**Domain**: System Audit
**Epic**: Audit Logging & Compliance
**Sprint**: Sprint 1 (Weeks 1-2)

## User Story

As a parking lot admin,
I want to view a searchable audit log of all system actions,
So that I can track who changed what data and when for accountability and troubleshooting.

## Acceptance Criteria

- **AC1**: Admin navigates to 系統設定 → 系統日誌, displays paginated audit log table with columns:
  - 時間 (Timestamp), 使用者 (User), 動作 (Action), 資料表 (Table), 記錄ID (Record ID), IP位址 (IP Address)
- **AC2**: "查看詳情" button opens modal with old_values/new_values JSON diff view
- **AC3**: Search filters: date range, user, action type, table, record ID
- **AC4**: "匯出" button downloads CSV with all filtered records
- **AC5**: Pagination: 50 records per page
- **AC6**: Default sort: reverse chronological (newest first)

## Business Rules

- Read-Only: Audit logs cannot be edited or deleted (enforced via application middleware + DB trigger)
- Retention: All logs retained indefinitely (min 3 years)
- Performance: Optimized for millions of records
- Privacy: Mask sensitive data in values

## UI Requirements

- **Screen**: `/admin/settings/audit-logs`
- **Table**: Responsive with sticky header
- **Filters**: Collapsible panel above table
- **Detail Modal**: Full-screen with JSON diff

## Source

- init_draft.md lines 30, 70, 128
- CLAUDE.md audit logging

## Dependencies

- US-AUDIT-002 (audit data exists)
- US-SEC-001 (admin auth)

## Test Data

- Customer update log: phone change from 0912345678 to 0912999888
- Agreement creation log: space A區-01, license ABC-1234
- CSV import log: 50 customers imported
