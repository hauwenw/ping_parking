# US-AUDIT-003: Export Audit Log to CSV

**Priority**: Must Have
**Phase**: Phase 1
**Domain**: System Audit
**Epic**: Audit Logging & Compliance
**Sprint**: Sprint 4 (Weeks 7-8)

## User Story

As a parking lot admin,
I want to export filtered audit logs to CSV format,
So that I can analyze historical data in Excel or share with auditors.

## Acceptance Criteria

- **AC1**: "匯出CSV" button generates CSV with all filtered records (not just current page)
- **AC2**: CSV columns: timestamp, user_email, action, table, record_id, old_values, new_values, ip_address
- **AC3**: CSV filename: `audit_log_YYYYMMDD_HHmmss.csv`
- **AC4**: Large exports (>10,000 records) show progress indicator and stream download without timeout
- **AC5**: UTF-8 with BOM encoding for Excel compatibility (Traditional Chinese displays correctly)
- **AC6**: Export respects applied filters
- **AC7**: Export button disabled when no records match (tooltip: "沒有可匯出的記錄")

## Business Rules

- Export Limit: Max 100,000 records per export
- Streaming: Use streaming CSV for large exports
- Audit Export Action: Export itself logged (action=EXPORT_AUDIT_LOG)
- Access Control: Admin only

## UI Requirements

- **Button**: "匯出CSV" in top-right next to filters
- **Progress**: Spinner with "正在匯出..." during export
- **Success**: Toast "審計日誌已匯出" with download link
- **Error**: If >100k records, show "匯出記錄過多，請縮小篩選範圍 (最多 100,000 筆)"

## Verification Method

- Filter by last 7 days → Export → Verify CSV contains only filtered
- Export 50,000 records → Verify downloads without timeout
- Export 150,000 records → Verify error message
- Open CSV in Excel → Verify Traditional Chinese displays correctly

## Source

- init_draft.md line 128
- CLAUDE.md audit logging

## Dependencies

- US-AUDIT-001 (view with filters)
- US-AUDIT-002 (audit data)

## Related Stories

- US-BULK-001 through US-BULK-006 (CSV patterns)
