# PRD Review — Remaining Issues

Issues #1–6 have been resolved. The following issues are tracked here for future action.

---

## #7. License Plate Validation Is Too Loose

**Risk**: LOW | **File**: `03-agreement/US-AGREE-003-require-license-plate.md`

US-AGREE-003 validates plates as "3-8 chars, alphanumeric + hyphens." This would accept nonsensical inputs like `---`, `AAA`, or `123`. Taiwan license plates have specific formats that always include both letters and digits (e.g., `ABC-1234`, `AB-1234`, `1234-AB`).

**Recommendation**: Tighten validation to require at least one letter AND at least one digit, in addition to the existing 3-8 character length rule. Example regex: `^(?=.*[A-Z])(?=.*[0-9])[A-Z0-9-]{3,8}$`

---

## #8. Audit Log Performance at Scale

**Risk**: MEDIUM | **Files**: `06-system-audit/US-AUDIT-001-view-audit-log.md`, `US-AUDIT-003-export-audit-log.md`

US-AUDIT-001 says "Performance: Optimized for millions of records" and US-AUDIT-003 allows up to 100k record exports, but no technical strategy is specified:

- No index strategy defined for the `system_logs` table (timestamp, action, table, user_id should all be indexed)
- No partitioning approach for large tables (e.g., monthly partitions by timestamp)
- No guidance on whether `old_values`/`new_values` JSONB fields should have GIN indexes
- No archive/retention strategy for old logs beyond "retained indefinitely (min 3 years)"

**Recommendation**: Add an implementation note to US-AUDIT-002 specifying:
- Indexes: `(timestamp DESC)`, `(action)`, `(table, record_id)`, `(user_id)`
- Consider table partitioning by month if log volume exceeds 1M rows/year
- No GIN index on JSONB fields for Phase 1 (unlikely to query by JSON content)

---

## #9. Missing Error States for Cross-Navigation

**Risk**: LOW | **Files**: `03-agreement/US-AGREE-008-cross-page-navigation.md`, `02-customer/US-CUST-005-link-to-agreement.md`

Cross-navigation stories define happy paths but don't specify what happens when:

- A linked record doesn't exist (e.g., UUID in URL is valid format but record not found)
- A linked space was deactivated
- Browser back button after a record was terminated

US-CUST-005 handles invalid `customerId` ("客戶不存在" + redirect), but similar handling is not documented for agreement detail, payment detail, or space detail pages.

**Recommendation**: Add a generic cross-navigation error rule to `09-ui-ux/README.md`:
- Invalid/missing record → Show "找不到此記錄" page with "返回列表" button
- Apply consistently to all detail pages (`/admin/customers/:id`, `/admin/agreements/:id`, etc.)

---

## #10. 09-ui-ux Directory Has No Detailed Stories

**Risk**: MEDIUM | **File**: `09-ui-ux/README.md`

The 09-ui-ux directory only has a README with page inventory. The 8 detailed UI stories (US-UI-001 through US-UI-008) are listed as "to be written after domain stories complete." Meanwhile, domain stories already embed specific UI details (button placements, modal behaviors, table columns, color coding).

This creates a risk of conflicting specifications when UI stories are eventually written.

**Recommendation**: Either:
1. Write the UI stories soon, consolidating scattered UI details from domain stories into a single source of truth per page, OR
2. Explicitly note in `09-ui-ux/README.md` that domain story UI sections are authoritative for Phase 1, and UI stories should only add layout/responsive/accessibility/component library details

---

## #11. No Pricing Model Definition

**Risk**: HIGH | **Affected stories**: `US-AGREE-001`, `US-AGREE-007`, `US-LOC-003` | **STATUS**: ✅ RESOLVED

**Resolution**: Created `US-SPACE-003-pricing-model.md` defining complete pricing architecture:

- **Three-tier hierarchy**: Site base price → Custom space price → Tag price (tag price wins if present)
- **Dual price points**: Monthly and daily rates stored separately at site/space/tag levels
- **Tag behavior**: Adding tag with price updates space immediately; removing tag keeps price
- **Agreement price**: Auto-calculated from space price but editable; immutable snapshot after creation
- **Change isolation**: Site/tag/space price changes don't affect existing agreements

Updated CLAUDE.md and US-AGREE-001 to reference the new pricing model.

---

## #12. Payment Model Is Underspecified

**Risk**: HIGH | **Affected stories**: `US-AGREE-001`, `US-AGREE-006` | **STATUS**: ✅ RESOLVED

**Resolution**: Created `US-PAY-001-payment-lifecycle.md` defining complete payment behavior:

- **Amount source**: Payment amount = agreement price (already includes tag effects)
- **Auto-generation**: One payment per agreement, created atomically with agreement
- **Payment editing**: Admin can edit amount after creation with required reason (logged to audit)
- **Termination impact**: Pending payments auto-voided; completed payments unchanged
- **Status lifecycle**: pending → completed / voided (no reactivation)
- **No partial payments**: Phase 1 supports one full payment per agreement only

Updated CLAUDE.md, US-AGREE-001, and US-AGREE-006 to reference the payment lifecycle.

---

## #13. Minor Inconsistencies in Chinese Terminology

**Risk**: LOW | **Files**: `US-CUST-001`, `US-LOC-002`

- **Phone field error messages differ**: US-CUST-001 uses "電話格式不正確 (09XX-XXX-XXX)" but US-LOC-002 uses "請輸入有效的台灣手機號碼 (格式: 09XX-XXX-XXX)". Should pick one and use consistently.
- **Phone field label differs**: US-CUST-001 uses "電話" as the field label, while US-LOC-002 uses "手機號碼" in error messages. Recommend standardizing on "電話" (shorter, used in forms) for the field label and keeping error messages consistent.
- **Customer README count mismatch**: README says "Total Stories: 6" but only 5 stories are listed in the summary table. Either a 6th story is missing or the count should be 5.

**Recommendation**: Standardize on:
- Field label: **電話**
- Error message: **"電話格式不正確 (09XX-XXX-XXX)"**
- Fix story count in customer README to 5

---

## Summary

| # | Issue | Risk | Status |
|---|-------|------|--------|
| 1 | Phone storage format contradiction | HIGH | Resolved |
| 2 | Missing customer delete story | MEDIUM | Resolved |
| 3 | Agreement renewal gap | MEDIUM | Resolved |
| 4 | Cron job single point of failure | HIGH | Resolved |
| 5 | Concurrent session restriction | MEDIUM | Resolved |
| 6 | Phone as sole unique identifier | MEDIUM | Resolved |
| 7 | License plate validation too loose | LOW | Open |
| 8 | Audit log performance at scale | MEDIUM | Open |
| 9 | Missing error states for cross-navigation | LOW | Open |
| 10 | UI stories directory empty | MEDIUM | Open |
| 11 | No pricing model definition | HIGH | ✅ Resolved |
| 12 | Payment model underspecified | HIGH | ✅ Resolved |
| 13 | Minor Chinese terminology inconsistencies | LOW | Open |
