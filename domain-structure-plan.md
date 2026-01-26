# Plan: Product Specification Domain Structure

## Objective
Reorganize the existing `init_draft.md` into 14 business-focused domain specification files for product managers. Focus on business logic and design, deferring technical implementation details.

## Context
- **Audience**: Product managers (business-first, not technical)
- **Development approach**: Feature-by-feature
- **Team structure**: Specialized roles
- **Priority**: Lock down business and design before technical specifications

## Proposed Domain Structure (14 Files)

### Core Business Domains (Feature-by-Feature)

#### 1. `docs/specs/00-product-overview.md`
**Purpose**: High-level vision and project foundation
**Content from init_draft.md**:
- Executive Summary (lines 4-13)
- User Roles (lines 33-37)
- Success Criteria (lines 211-220)
- Implementation Timeline (lines 173-182)
- Future Roadmap (lines 198-208)
- Business glossary (NEW - define terms like "tag", "agreement type", "space status")

#### 2. `docs/specs/01-parking-space-management.md`
**Purpose**: Physical parking infrastructure and categorization
**Content from init_draft.md**:
- Multi-location management
- Space creation and naming
- Tag system (lines 24, flexible categorization)
- Pricing multipliers (line 118)
- Space status lifecycle (NEW - detail needed)
- Business rules: one space = one active agreement (lines 76-77)

#### 3. `docs/specs/02-customer-management.md`
**Purpose**: Customer data and privacy compliance
**Content from init_draft.md**:
- Customer data requirements (line 65: name, phone, email, notes)
- Active agreement count tracking (line 65: computed field)
- Privacy compliance - NO national ID (line 126)
- Customer lifecycle (NEW - detail needed)
- Data validation rules (phone format line 156, email)
- Deduplication policies (NEW - detail needed)

#### 4. `docs/specs/03-agreement-management.md`
**Purpose**: Rental contract lifecycle and rules
**Content from init_draft.md**:
- Agreement types: daily/monthly/quarterly/yearly (lines 26, 67)
- License plate requirement - MANDATORY for all types (lines 8, 26, 67)
- Agreement lifecycle: pending → active → expired/terminated (line 67)
- Date calculation rules (NEW - detail needed: +1mo, +3mo, +1yr, +1d)
- Space-agreement relationship (1:1 when active, lines 76-77)
- Start date and end date logic (line 67)
- Termination policies (NEW - detail needed)
- Cannot delete agreements with payments (NEW - from CLAUDE.md)

#### 5. `docs/specs/04-payment-tracking.md`
**Purpose**: Payment recording and reconciliation
**Content from init_draft.md**:
- Payment model: one payment per agreement (lines 27, 68)
- Manual offline payment recording (line 27)
- Bank reference requirements (line 68)
- Payment status: pending/completed/refunded (line 68)
- Payment date vs agreement start date (NEW - can differ)
- Late payment handling (line 167: Late Payments report)
- Payment-agreement relationship (1:1, lines 76-77)

#### 6. `docs/specs/05-waiting-list.md`
**Purpose**: Queue management and space allocation
**Content from init_draft.md**:
- FIFO queue per site (lines 29, 97)
- Manual allocation workflow (line 29)
- Space allocation process (lines 104-107)
- Priority management (NEW - detail needed)
- Removal rules after allocation (NEW - detail needed)
- Independent workflow (line 97)

#### 7. `docs/specs/06-system-audit.md`
**Purpose**: Audit logging and compliance
**Content from init_draft.md**:
- What gets logged: all admin actions (lines 30, 70, 128)
- Audit trail structure (line 70: action, user_id, table, record_id, old_values, new_values, timestamp, ip_address)
- Data retention policies (NEW - detail needed)
- Compliance requirements (lines 124-135)
- Privacy requirements (line 126: no national ID, line 129: license plates encrypted)

#### 8. `docs/specs/07-bulk-operations.md`
**Purpose**: CSV import/export and data migration
**Content from init_draft.md**:
- 6 CSV import formats (lines 31, 109-114):
  1. Customers
  2. Spaces
  3. Agreements
  4. Payments
  5. Tags
  6. Waiting List
- CSV import workflow (lines 109-114)
- Template specifications (line 110)
- Validation rules (line 111)
- Error handling (line 111: show errors)
- Progress tracking (line 112)
- Import log and retry (line 113)
- Success criteria: 100% data migration (line 219)

### Cross-Cutting Specifications

#### 9. `docs/specs/08-user-workflows.md`
**Purpose**: End-to-end user journeys
**Content from init_draft.md**:
- Space allocation workflow (lines 104-107)
- Customer onboarding (NEW - detail needed)
- Agreement creation (lines 104-107)
- Payment recording (line 107: auto-generate payment record)
- Waiting list to allocation (lines 104-107)
- Agreement renewal (NEW - detail needed)
- Customer notification (line 107)

#### 10. `docs/specs/09-ui-ux-specifications.md`
**Purpose**: All screens, navigation, and design system
**Content from init_draft.md**:
- Navigation menu (line 86: 8 pages)
  1. 儀表板 (Dashboard)
  2. 停車場管理 (Site Management)
  3. 客戶管理 (Customer Management)
  4. 合約管理 (Agreement Management)
  5. 付款管理 (Payment Management)
  6. 候補名單 (Waiting List)
  7. 系統設定 (System Settings)
  8. 報表 (Reports)
- Page specifications (lines 90-97)
- Cross-page navigation (lines 12, 95-96)
- Color system (lines 142-147)
- Responsive design (lines 149-152)
- Design patterns: grid layout, color blocks, tag dots, hover details (lines 92-93)

#### 11. `docs/specs/10-localization-design.md`
**Purpose**: Traditional Chinese and Taiwan-specific requirements
**Content from init_draft.md**:
- Traditional Chinese localization (line 154-158)
- Taiwan phone format: 09XX-XXX-XXX (line 156)
- TWD currency format: NT$1,234 (line 157)
- Taiwan date formats (line 158)
- All UI labels and buttons (line 155)
- Validation messages (NEW - all in Traditional Chinese)
- Error messages (NEW - all in Traditional Chinese)
- Notification templates (line 155, SMS/Email from line 43)

#### 12. `docs/specs/11-reporting-requirements.md`
**Purpose**: Reports, dashboards, and analytics
**Content from init_draft.md**:
- 4 core reports (lines 164-169):
  1. Occupancy Dashboard (real-time, spaces by tag, site utilization)
  2. Late Payments (daily, overdue agreements)
  3. Revenue Summary (monthly, total active agreements)
  4. Customer Summary (monthly, active customers, avg agreements)
- Report layouts (NEW - detail needed)
- Export formats (NEW - detail needed)
- KPIs and metrics definitions (lines 166-169)
- Print-friendly reports (line 152)

### Reference Documents

#### 13. `docs/specs/12-data-model.md`
**Purpose**: Conceptual data model and business constraints
**Content from init_draft.md**:
- 12 core tables overview (lines 63-71)
- Entity relationships (lines 74-77)
- Business constraints (NOT implementation):
  - Each space: ONE active agreement only
  - Customer → Agreements (1:N)
  - Agreement → Payment (1:1)
  - Space → Tags (M:N via array)
- Key fields per entity (lines 65-70)
- Computed fields (line 65: active_agreement_count)

#### 14. `docs/specs/13-technical-context.md`
**Purpose**: Minimal technical overview (to be expanded later)
**Content from init_draft.md**:
- Technology stack overview (lines 47-55)
- Architecture diagram (lines 42-44)
- Cost structure (lines 57, 186-194)
- Deployment environment (Vercel, line 55)
- Security overview (lines 124-135)
- Note: "Detailed technical implementation specs to be defined in later phases"

## File Organization

```
/Users/howardwu/repos/ping_parking/
├── init_draft.md (existing - to be archived)
├── CLAUDE.md (existing - developer guide)
└── docs/
    └── specs/
        ├── 00-product-overview.md
        ├── 01-parking-space-management.md
        ├── 02-customer-management.md
        ├── 03-agreement-management.md
        ├── 04-payment-tracking.md
        ├── 05-waiting-list.md
        ├── 06-system-audit.md
        ├── 07-bulk-operations.md
        ├── 08-user-workflows.md
        ├── 09-ui-ux-specifications.md
        ├── 10-localization-design.md
        ├── 11-reporting-requirements.md
        ├── 12-data-model.md
        └── 13-technical-context.md
```

## Execution Plan

### Phase 1: Create Directory Structure
1. Create `docs/specs/` directory
2. Keep `init_draft.md` as reference (don't delete)

### Phase 2: Extract and Expand Content (Feature-by-Feature Order)
For each domain file:
1. Extract relevant sections from `init_draft.md`
2. Identify gaps marked as "NEW - detail needed"
3. Expand with product manager-friendly detail
4. Add examples, edge cases, business rules
5. Include wireframes/mockups for UI specs

**Recommended Creation Order**:
1. 00-product-overview.md (foundation)
2. 12-data-model.md (entities and relationships)
3. 01-parking-space-management.md (core domain)
4. 02-customer-management.md (core domain)
5. 03-agreement-management.md (core domain - depends on 01, 02)
6. 04-payment-tracking.md (depends on 03)
7. 05-waiting-list.md (depends on 01, 02)
8. 08-user-workflows.md (synthesizes 01-05)
9. 09-ui-ux-specifications.md (all screens)
10. 10-localization-design.md (UI copy)
11. 11-reporting-requirements.md (analytics)
12. 06-system-audit.md (cross-cutting)
13. 07-bulk-operations.md (data integration)
14. 13-technical-context.md (minimal tech overview)

### Phase 3: Cross-Reference and Validate
1. Ensure consistency across domains
2. Verify all business rules are documented
3. Check for gaps or contradictions
4. Add cross-references between related domains

## Key Principles

1. **Business-First**: Focus on WHAT the system does, not HOW it's built
2. **Product Manager Friendly**: No code, no database syntax, no framework specifics
3. **Complete**: Fill in all "NEW - detail needed" gaps
4. **Visual**: Include diagrams, workflows, wireframes where helpful
5. **Localized**: All UI examples in Traditional Chinese
6. **Testable**: Clear acceptance criteria for each feature

## Gaps to Address During Extraction

Based on `init_draft.md` review, these need expansion:
- Customer lifecycle states
- Space status lifecycle (available/occupied/maintenance)
- Agreement date calculation formulas
- Agreement termination policies
- Customer deduplication rules
- Waiting list priority rules
- Removal from waiting list after allocation
- Agreement renewal workflow
- Customer onboarding workflow
- Report layouts and export formats
- Detailed page wireframes for all 8 pages
- All Traditional Chinese UI copy
- Error message catalog
- Notification templates (SMS/Email)
- Tag pricing multiplier calculation examples

## Next Steps

1. User approves this structure
2. Begin creating files in recommended order
3. Iteratively review and refine each domain specification
4. Once all 14 files are complete and approved, proceed to technical design phase
