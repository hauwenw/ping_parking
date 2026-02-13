# UI/UX Specifications - Ping Parking Management System

**Total Stories**: 8 (planned)
**Status**: **Phase 2** — UI requirements are currently embedded in each domain story. Separate UI stories will be written when needed for advanced layout, responsive design, and component library specifications.

## Overview

This directory defines the user interface and user experience for the admin web application. The UI overview below establishes page structure and navigation. Detailed UI stories (US-UI-001 through US-UI-008) are deferred to Phase 2 since each domain story already contains its own UI requirements section.

**Purpose of This Document**: Provide page inventory and URL structure so domain stories can reference pages consistently.

---

## Terminology

To avoid confusion, this document uses the following terms consistently:

| Term | Traditional Chinese | Definition | Example |
|------|---------------------|------------|---------|
| **Site** | 停車場 | A physical parking lot location managed by the Wu family | "A區停車場", "B區停車場", "C區停車場" |
| **Space** | 車位 | An individual parking spot within a site for one vehicle | "A-01", "A-02", "B-15" |
| **Customer** | 客戶 | Person or company renting a parking space | "王小明", "李小華" |
| **Agreement** | 合約 / 租約 | Rental contract linking customer + space + dates | "Monthly agreement for A-01, Feb 1-28" |
| **Tag** | 標籤 | Flexible label for space attributes | "有屋頂", "VIP", "大車位" |

**Example Hierarchy**:
```
Ping Parking System
├── A區停車場 (Site A)
│   ├── A-01 (Space) - 有屋頂, VIP
│   ├── A-02 (Space) - 有屋頂
│   └── A-03 (Space)
├── B區停車場 (Site B)
│   ├── B-01 (Space)
│   └── B-02 (Space) - 大車位
└── C區停車場 (Site C)
    └── C-01 (Space)
```

**Total**: 3 sites, ~100 spaces across all sites

---

## Page Inventory (Phase 1 - Must Have)

| # | Page Name | URL | Purpose | Related Stories |
|---|-----------|-----|---------|-----------------|
| 1 | 儀表板 (Dashboard) | `/admin/dashboard` | Landing page with KPIs, occupancy stats, alerts | US-UI-001 |
| 2 | 停車場管理 (Site Management) | `/admin/sites/:siteId` | Space grid with tag dots, occupancy indicators | US-UI-002 |
| 3 | 客戶管理 - 列表 (Customer List) | `/admin/customers` | Customer table with search/filter | US-UI-003 |
| 4 | 客戶詳情 (Customer Detail) | `/admin/customers/:customerId` | Customer info + agreements tab | US-UI-004 |
| 5 | 合約管理 - 列表 (Agreement List) | `/admin/agreements` | Agreement table with filters | US-UI-005 |
| 6 | 合約詳情 (Agreement Detail) | `/admin/agreements/:agreementId` | Agreement info + cross-links | US-UI-006 |
| 7 | 付款管理 (Payment Management) | `/admin/payments` | Payment tracking table | US-UI-007 |
| 8 | 系統設定 (System Settings) | `/admin/settings` | Tag configuration, admin preferences | US-UI-008 |

**Future Pages (Should Have - Phase 2)**:
- 候補名單 (Waiting List): `/admin/waiting-list`
- 報表 (Reports): `/admin/reports`
- CSV 匯入 (CSV Import): `/admin/import`

---

## Navigation Structure

### Primary Navigation (Desktop - Top Bar)
```
儀表板 | 停車場管理 | 客戶管理 | 合約管理 | 付款管理 | 系統設定
```

### Page Hierarchy
```
/ (redirect to /admin/dashboard)
└── /admin
    ├── /dashboard                    # Landing page
    ├── /sites/:siteId                # Site management (grid view)
    ├── /customers                    # Customer list
    │   └── /:customerId              # Customer detail
    │       └── Tab: 合約記錄          # Agreements tab on customer detail
    ├── /agreements                   # Agreement list
    │   └── /:agreementId             # Agreement detail
    ├── /payments                     # Payment list
    └── /settings                     # System settings
        └── Tab: 標籤管理              # Tags tab
```

---

## Page Relationships (Cross-Navigation)

### Customer → Agreement → Payment Flow
1. **Customer List** (`/admin/customers`) → Click row → **Customer Detail** (`/admin/customers/:customerId`)
2. **Customer Detail** → 合約記錄 tab (shows agreements table) → Click row → **Agreement Detail** (`/admin/agreements/:agreementId`)
3. **Agreement Detail** → Payment section → Click "查看付款詳情" → **Payment Detail** (inline or modal)

### Site → Space → Agreement Flow
1. **Site Management** (`/admin/sites/:siteId`) → Click space → **Space Detail Modal** (or inline panel)
2. **Space Detail** → Shows current agreement → Click agreement link → **Agreement Detail** (`/admin/agreements/:agreementId`)

### Agreement → Customer & Space (Reverse Navigation)
1. **Agreement Detail** → Customer name (clickable link) → **Customer Detail**
2. **Agreement Detail** → Space name (clickable link) → **Site Management** (filtered to that space)

### Breadcrumb Pattern
All detail pages show breadcrumbs:
- Customer Detail: `首頁 > 客戶管理 > 王小明`
- Agreement Detail: `首頁 > 合約管理 > 合約詳情 (AGR-001)`
- Site Management: `首頁 > 停車場管理 > A區停車場`

---

## UI Patterns & Components (High-Level)

### Common Patterns
- **List Pages**: Table with search, filters, pagination, "新增" button
- **Detail Pages**: Card-based sections with header (ID/status/actions), info cards, audit trail
- **Forms**: Modal overlays for create/edit operations
- **Cross-Links**: Blue underlined links (hover: darker), open in same tab
- **Status Badges**: Color-coded pills (blue=pending, green=active, gray=expired/terminated)
- **Tag Dots**: Colored circles on space grids for quick visual scanning

### Responsive Design
- **Desktop-first**: Optimized for 1920x1080 (primary use case: office desktop)
- **Tablet**: 1024x768 minimum (secondary use case: iPad at parking lot)
- **Mobile**: Not required for Phase 1 (admin-only)

### Color Scheme (Preliminary)
- Primary: Blue (links, pending status)
- Success: Green (active agreements, occupied spaces)
- Warning: Yellow (alerts, approaching due dates)
- Neutral: Gray (expired/terminated agreements, available spaces)
- Error: Red (validation errors, late payments)

---

## URL Conventions

### Resource Naming
- Plural nouns for collections: `/customers`, `/agreements`, `/payments`
- UUID for IDs: `/customers/550e8400-e29b-41d4-a716-446655440000`
- Kebab-case for multi-word: `/waiting-list`, `/system-logs`

### Query Parameters (Filters)
- Date range: `?start_date=2026-02-01&end_date=2026-03-01`
- Status: `?status=active,pending` (comma-separated for multiple)
- Search: `?q=王小明` (URL-encoded Traditional Chinese)
- Pagination: `?page=2&limit=20`

### Deep Linking
All pages support direct URL access:
- Share link to specific agreement: `/admin/agreements/AGR-12345`
- Filtered customer list: `/admin/customers?status=active&q=王`
- Site with space highlighted: `/admin/sites/SITE-A?space=A-01`

---

## Accessibility & Localization

### Language
- **All UI text**: Traditional Chinese (Taiwan)
- **Number format**: Arabic numerals with Chinese units (1,234 車位)
- **Currency**: NT$1,234 (comma separators)
- **Date format**: YYYY-MM-DD (ISO) in forms, YYYY年MM月DD日 for display
- **Phone format**: 09XX-XXX-XXX (with hyphen validation)

### Accessibility (WCAG 2.1 AA)
- Keyboard navigation support (Tab, Enter, Esc)
- Focus indicators on all interactive elements
- Color contrast ratio ≥ 4.5:1
- Screen reader labels (aria-label for icons)

---

## Notes for Domain Story Writers

When writing domain stories (Customer, Space, Payment, etc.), reference pages using this format:

**Example**:
```markdown
## UI Requirements
**Page**: 客戶管理 - 列表 (see 09-ui-ux/README.md)
**Action**: Click "新增客戶" button → Modal form opens
**Validation**: Inline error messages below each field
**Success**: Modal closes, table refreshes, toast: "客戶已新增"

**Cross-Navigation**: Customer name is clickable link → 客戶詳情 page (see 09-ui-ux/README.md for page structure)
```

---

## Detailed UI Stories (To Be Written Later)

The following stories will be written AFTER all domain stories are complete:

1. **US-UI-001**: Dashboard Overview (KPIs, alerts, quick actions)
2. **US-UI-002**: Site Management Grid (space layout, tag dots, filters)
3. **US-UI-003**: Customer List Page (table, search, filters, create button)
4. **US-UI-004**: Customer Detail Page (tabs, agreement history, edit actions)
5. **US-UI-005**: Agreement List Page (filters, status badges, cross-links)
6. **US-UI-006**: Agreement Detail Page (card sections, terminate action, cross-navigation)
7. **US-UI-007**: Payment Management Page (table, status tracking, filters)
8. **US-UI-008**: System Settings Page (tag configuration, admin preferences)

**Estimated Effort**: 6-8 hours (written after domain clarity in Sprint 4)

---

## Dependencies

This UI overview establishes structure for:
- **Agreement Stories**: US-AGREE-005 (view detail), US-AGREE-008 (cross-navigation)
- **Customer Stories**: US-CUST-002 (view detail), US-CUST-003 (edit)
- **Space Stories**: US-SPACE-002 (grid view), US-SPACE-005 (tag filtering)
- **Payment Stories**: US-PAY-002 (record payment), US-PAY-003 (view history)

All domain stories can now reference pages defined in this document.

---

**Last Updated**: 2026-01-25 (Week 0 - Planning Phase)
**Status**: Page inventory complete. Detailed UI stories pending domain completion.
