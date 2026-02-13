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
