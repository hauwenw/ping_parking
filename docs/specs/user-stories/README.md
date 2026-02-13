# User Stories - Ping Parking Management System

## Overview

This directory contains comprehensive, feature-level user stories derived from `init_draft.md` requirements. These stories guide Phase 1 development with a focus on business value, clear acceptance criteria, and MoSCoW prioritization.

**Phase 1 MVP Stories**: 35 (all Must Have) — See `docs/specs/mvp-scope.md`
**Phase 2 Stories**: To be written (waiting list, bulk operations, reporting, etc.)

## Story Organization

Stories are organized into domain-specific directories with **one file per story** for better readability and version control:

```
docs/specs/user-stories/
├── README.md (this file)
├── 01-space/              # Parking Space Management (6 stories) ✅ MVP
│   ├── README.md
│   ├── US-SPACE-001-site-configuration.md
│   ├── US-SPACE-002-manage-spaces.md
│   ├── US-SPACE-003-pricing-model.md
│   ├── US-SPACE-004-tag-management.md
│   ├── US-SPACE-005-space-list-view.md
│   └── US-SPACE-006-view-space-detail.md
├── 02-customer/           # Customer Management (5 stories) ✅ MVP
│   ├── README.md
│   ├── US-CUST-001-create-customer.md
│   ├── US-CUST-002-view-customer-detail.md
│   ├── US-CUST-003-edit-customer.md
│   ├── US-CUST-004-search-filter-customers.md
│   └── US-CUST-005-link-to-agreement.md
├── 03-agreement/          # Agreement Management (9 stories) ✅ MVP
│   ├── README.md
│   ├── US-AGREE-001-create-monthly-agreement.md
│   ├── US-AGREE-002-auto-calculate-end-dates.md
│   ├── ... (5 more stories)
│   └── US-AGREE-009-agreement-list-view.md  ← includes payment status
├── 04-payment/            # Payment Management (2 stories) ✅ MVP
│   ├── README.md
│   ├── US-PAY-001-payment-lifecycle.md
│   └── US-PAY-002-record-payment.md
├── 06-system-audit/       # System Audit (3 stories) ✅ MVP
│   ├── README.md
│   ├── US-AUDIT-001-view-audit-log.md
│   ├── US-AUDIT-002-auto-log-actions.md
│   └── US-AUDIT-003-export-audit-log.md
├── 09-ui-ux/              # UI/UX Specifications 📅 Phase 2
│   └── README.md (page inventory only)
├── 10-localization/       # Localization (4 stories) ✅ MVP
│   ├── README.md
│   ├── US-LOC-001-traditional-chinese-ui.md
│   ├── US-LOC-002-taiwan-phone-format.md
│   ├── US-LOC-003-twd-currency-format.md
│   └── US-LOC-004-taiwan-date-format.md
└── 12-security/           # Security & Auth (6 stories) ✅ MVP
    ├── README.md
    ├── US-SEC-001-admin-authentication.md
    ├── US-SEC-002-session-management.md
    └── ... (4 more stories)
```

### Phase 1 MVP Domains (35 stories written)

| Directory | Domain | Story Count | Status |
|-----------|--------|-------------|--------|
| `01-space/` | Parking Space Management | 6 | ✅ Complete |
| `02-customer/` | Customer Management | 5 | ✅ Complete |
| `03-agreement/` | Agreement Management | 9 | ✅ Complete |
| `04-payment/` | Payment Management | 2 | ✅ Complete |
| `06-system-audit/` | System Audit | 3 | ✅ Complete |
| `10-localization/` | Localization | 4 | ✅ Complete |
| `12-security/` | Security & Auth | 6 | ✅ Complete |

### Phase 2 Domains (stories not yet written)

| Domain | Estimated Stories | Status | Reason Deferred |
|--------|-------------------|--------|-----------------|
| `05-waiting-list/` | ~3-4 | 📅 Phase 2 | Not critical for launch — can manage informally |
| `07-bulk-operations/` | ~3-4 | 📅 Phase 2 | Manual entry sufficient for ~100 spaces at launch |
| `08-user-workflows/` | ~1-2 | 📅 Phase 2 | Core workflows already embedded in domain stories |
| `09-ui-ux/` | ~8 | 📅 Phase 2 | UI requirements already specified in each domain story |
| `11-reporting/` | ~2-3 | 📅 Phase 2 | Payment list + space list serve as interim reporting |

## Story Numbering Scheme

### Format

**Pattern**: `US-[DOMAIN]-[Sequence]`

- **US**: User Story prefix
- **DOMAIN**: 3-6 letter domain identifier
- **Sequence**: Zero-padded 3-digit number (001, 002, ...)

### Domain Prefixes

| Prefix | Domain | Example |
|--------|--------|---------|
| `SPACE` | Parking Space Management | US-SPACE-001 |
| `CUST` | Customer Ma  nagement | US-CUST-001 |
| `AGREE` | Agreement Management | US-AGREE-001 |
| `PAY` | Payment Tracking | US-PAY-001 |
| `WAIT` | Waiting List | US-WAIT-001 |
| `AUDIT` | System Audit | US-AUDIT-001 |
| `BULK` | Bulk Operations | US-BULK-001 |
| `FLOW` | User Workflows | US-FLOW-001 |
| `UI` | UI/UX | US-UI-001 |
| `LOC` | Localization | US-LOC-001 |
| `RPT` | Reporting | US-RPT-001 |
| `SEC` | Security & Auth | US-SEC-001 |

### Numbering Examples

```
US-SPACE-001: Create parking space with tags
US-CUST-001: Register new customer
US-AGREE-001: Create monthly rental agreement
US-PAY-001: Record offline payment
US-FLOW-001: Complete space allocation workflow
US-UI-001: View dashboard with tag-based statistics
US-LOC-002: Display phone numbers in Taiwan format
US-RPT-001: Generate occupancy dashboard report
US-SEC-001: Admin authentication with Supabase Auth
```

## MoSCoW Prioritization

### Phase 1 MVP (35 stories)

**Definition**: Essential features for the system to launch and support core parking lot operations.

**Domains**: Space, Customer, Agreement, Payment, Audit, Localization, Security

**Sprint Allocation**: 4 sprints across 8 weeks (~9 stories per sprint)

---

### Phase 2 (stories not yet written)

**Definition**: Important features that enhance operations but are not required for launch.

**Planned Domains**:
- **Waiting list**: FIFO queue per site, manual allocation
- **Bulk operations**: CSV import for 6 entity types
- **Reporting**: Occupancy dashboard, revenue/late payment reports
- **UI/UX stories**: Separate UI specs (currently embedded in domain stories)
- **User workflows**: Separate end-to-end journey documentation

---

### Phase 3+ (Roadmap)

**Definition**: Out of scope; requires major investment or external dependencies.

**Examples**:
- Payment gateway integration
- Hardware integration (gates, cameras)
- Mobile app for site managers
- Multi-language support (beyond Traditional Chinese)

## Story Templates

### Template A: Feature Story (Core CRUD)

Use for: Creating, reading, updating, or deleting entities (spaces, customers, agreements, payments, tags)

```markdown
**US-[DOMAIN]-[NUM]: [Verb] [Entity] [Context]**

As a [parking lot admin],
I want to [perform action],
So that [business value/outcome].

**Priority**: [Must Have / Should Have / Could Have / Won't Have]
**Phase**: [Phase 1 / Phase 2 / Phase 3]
**Domain**: [Domain Name]
**Epic**: [Epic Name] (if applicable)

**Acceptance Criteria**:
- **AC1**: Given [precondition], when [action], then [expected outcome]
- **AC2**: Given [precondition], when [action], then [expected outcome]
- **AC3**: System logs [action] to audit trail with [specific fields]
- **AC4**: Error handling: [specific validation rules in Traditional Chinese]

**Business Rules**:
- [Key constraint or rule from domain spec]
- [Reference to related story dependencies]

**UI Requirements** (if applicable):
- [Screen/component affected]
- [Specific UI elements or interactions]

**Source**: init_draft.md lines [XXX-YYY]
**Dependencies**: [Related story IDs]
**Test Data**: [Example data needed]
```

---

### Template B: Workflow Story (Cross-Domain)

Use for: End-to-end user journeys that span multiple entities (space allocation, CSV import, customer onboarding)

```markdown
**US-FLOW-[NUM]: [Complete Workflow Name]**

As a [parking lot admin],
I want to [complete end-to-end process],
So that [business outcome].

**Priority**: [Must Have / Should Have / Could Have / Won't Have]
**Phase**: [Phase 1]
**Domain**: User Workflows (Cross-domain)
**Epic**: [Workflow Epic Name]

**Workflow Steps**:
1. [Step 1 description] → Triggers [US-DOMAIN-XXX]
2. [Step 2 description] → Triggers [US-DOMAIN-YYY]
3. [Step 3 description] → Triggers [US-DOMAIN-ZZZ]
4. [Final outcome]

**Acceptance Criteria**:
- **AC1**: Admin can complete entire workflow from [entry point] to [completion]
- **AC2**: System validates [business rule] at step [X]
- **AC3**: System auto-generates [related record] after step [Y]
- **AC4**: All workflow steps logged to audit trail

**Source**: init_draft.md lines [XXX-YYY]
**Dependencies**: [All related story IDs]
**Related Stories**: [List of dependent stories]
```

---

### Template C: Non-Functional Requirement (NFR) Story

Use for: Quality attributes (performance, security, compliance, localization)

```markdown
**US-[DOMAIN]-[NUM]: [NFR Type] - [Specific Requirement]**

As a [system/admin/customer],
I want the system to [quality attribute],
So that [compliance/performance/usability goal].

**Priority**: [Must Have / Should Have / Could Have / Won't Have]
**Phase**: [Phase 1]
**Domain**: [Localization / Security / Audit]
**Type**: [NFR: Performance / Security / Compliance / Localization]

**Acceptance Criteria**:
- **AC1**: [Measurable criterion with specific threshold]
- **AC2**: [Compliance requirement with standard reference]
- **AC3**: [Performance target with measurement method]

**Verification Method**:
- [How to test/validate this NFR]

**Source**: init_draft.md lines [XXX-YYY]
**Related Stories**: [Stories implementing this NFR]
```

---

### Template D: UI/UX Story

Use for: User interface screens, components, and interactions

```markdown
**US-UI-[NUM]: [Screen/Component Name] - [Specific Interaction]**

As a [parking lot admin],
I want to [view/interact with UI element],
So that [task efficiency/information access].

**Priority**: [Must Have / Should Have / Could Have / Won't Have]
**Phase**: [Phase 1]
**Domain**: UI/UX Specifications
**Screen**: [儀表板 / 停車場管理 / etc.]

**Acceptance Criteria**:
- **AC1**: Screen displays [specific data elements] in [layout]
- **AC2**: User can [specific interaction] with [visual feedback]
- **AC3**: Screen is responsive on [device sizes: desktop/tablet]
- **AC4**: All labels and messages in Traditional Chinese

**Design Requirements**:
- **Layout**: [Grid/list/table structure]
- **Colors**: [Tag colors, status colors]
- **Interactions**: [Click/hover behaviors]

**Source**: init_draft.md lines [XXX-YYY], UI/UX specs
**Related Data Stories**: [Backend stories providing data]
```

## Story Status Legend

| Status | Symbol | Meaning |
|--------|--------|---------|
| **Planned** | ⏳ | Story defined but not yet in development |
| **In Progress** | 🔄 | Actively being developed |
| **Done** | ✅ | Story complete, tested, and merged |
| **Blocked** | ⛔ | Waiting on dependencies or external factors |
| **Deferred** | 📅 | Moved to later sprint or phase |

## How to Navigate This Structure

### Finding Stories

**By Domain**: Browse domain directories (e.g., `03-agreement/`) and read the domain README for overview

**By Story ID**: Stories follow pattern `US-{DOMAIN}-{NUM}-{brief-title}.md`
- Example: `US-AGREE-001-create-monthly-agreement.md`

**By Sprint**: Check domain READMEs for sprint allocation tables

**Quick Reference**: Each domain README provides a summary table with all stories, priorities, and sprint assignments

### Story File Format

Each story file contains:
- User Story (As a... I want... So that...)
- Acceptance Criteria (AC1, AC2, ...)
- Business Rules
- UI Requirements
- Source references (init_draft.md line numbers)
- Dependencies (other story IDs)
- Test Data examples

## How to Use These Stories

### For Product Managers

1. **Prioritization**: Use MoSCoW categories to adjust scope if timeline changes
2. **Sprint Planning**: Check domain READMEs for sprint allocation, reference `story-map.md` for epic grouping
3. **Stakeholder Communication**: Share individual story files as requirements documentation
4. **Acceptance Testing**: Use acceptance criteria to validate implementations
5. **Navigation**: Start with domain README → Pick specific story file

### For Developers

1. **Implementation Guide**: Each story has source references to init_draft.md and domain specs
2. **Dependencies**: Check "Dependencies" section before starting a story
3. **Test Data**: Use provided test data examples for development and QA
4. **Business Rules**: Review business rules section to understand constraints
5. **File Links**: Stories link to related stories by ID (e.g., "depends on US-CUST-001")

### For QA/Testers

1. **Test Cases**: Convert acceptance criteria into test cases (one story = one test file)
2. **Validation**: Use "Verification Method" in NFR stories for testing approach
3. **Traditional Chinese**: Verify all UI copy matches acceptance criteria
4. **Cross-References**: Check traceability matrix to ensure all init_draft.md requirements covered
5. **Isolation**: Test each story independently using its test data

## Traceability

All user stories are mapped to:

1. **Source Requirements**: init_draft.md line numbers
2. **Domain Specifications**: 14-file spec structure (when created)
3. **Sprint Allocation**: See `story-map.md`
4. **Coverage Analysis**: See `traceability-matrix.md`

## Related Documents

- **`story-map.md`**: Epic grouping, sprint plan, release milestones
- **`traceability-matrix.md`**: Requirements coverage matrix linking stories to init_draft.md
- **`/docs/specs/00-product-overview.md`** (future): High-level product vision
- **`/docs/specs/01-parking-space-management.md`** (future): Detailed domain spec for parking spaces
- **`init_draft.md`**: Original product specification (root directory)
- **`CLAUDE.md`**: Developer guidance for implementation

## Success Criteria

✅ **MVP Coverage**: 35 stories covering all core CRUD operations for parking management
✅ **Clear Phasing**: MVP (Phase 1) vs deferred (Phase 2) clearly separated
✅ **Traceability**: Every story links back to init_draft.md source lines
✅ **Consistent Format**: All stories follow appropriate template
✅ **Acceptance Criteria**: Every story has specific, testable ACs
✅ **Traditional Chinese**: All UI-related ACs include Chinese copy
✅ **Dependencies**: All cross-story dependencies documented
✅ **Test Data**: All stories include concrete test data examples

## Contributing

When adding new stories:

1. Choose appropriate template based on story type
2. Assign unique story ID following numbering scheme
3. Map to source requirement in init_draft.md
4. Include 3-5 specific, testable acceptance criteria
5. Document dependencies to other stories
6. Add test data examples
7. Update traceability-matrix.md

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-01-24 | Initial user story structure created | Claude Code |

---

**Last Updated**: 2026-01-24
**Status**: ⏳ In Progress (46 Must Have stories to be written first)
**Contact**: Wu Family Operations Team
