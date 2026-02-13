# Parking Space Management Stories

**Total Stories**: 6 (all Must Have)
**Sprint**: Sprint 1 (4 stories) + Sprint 2 (2 stories)

## Must Have Stories

| ID | Story | Priority | Sprint |
|----|-------|----------|--------|
| US-SPACE-001 | Site Configuration (CRUD) | Must Have | Sprint 1 |
| US-SPACE-002 | Create/Edit/Delete Spaces | Must Have | Sprint 1 |
| US-SPACE-003 | Pricing Model (Base + Tag + Custom) | Must Have | Sprint 2 |
| US-SPACE-004 | Tag Management (CRUD) | Must Have | Sprint 1 |
| US-SPACE-005 | Space List View (Table with Filters) | Must Have | Sprint 2 |
| US-SPACE-006 | View Space Detail | Must Have | Sprint 2 |

## Overview

Physical parking infrastructure management covering 3 parking lots with ~100 total spaces. Includes site configuration with address and naming prefix, space creation with enforced naming format, flexible tag-based categorization with optional pricing, and comprehensive list/detail views with computed and manual status.

**Key Dependencies**: Tag system (flexible categorization + pricing), Agreement Management (occupancy), Payment Management (payment status display)
**Estimated Effort**: 15-18 story points

## Critical Business Rules

### Site Model
```
sites table:
├── id (UUID, primary key)
├── name (TEXT, unique) - e.g., "A區停車場"
├── prefix (TEXT, unique, immutable) - e.g., "A"
├── address (TEXT) - Site address
├── monthly_base_price (INTEGER) - Default monthly rate in NT$
├── daily_base_price (INTEGER) - Default daily rate in NT$
├── is_active (BOOLEAN) - Soft deactivation
├── created_at (TIMESTAMPTZ)
└── updated_at (TIMESTAMPTZ)
```

### Space Model
```
spaces table:
├── id (UUID, primary key)
├── site_id (UUID, foreign key → sites)
├── name (TEXT, unique per site) - Enforced format: {prefix}-{01-99}
├── tags (TEXT[]) - PostgreSQL array, e.g., ['有屋頂', 'VIP']
├── monthly_price (INTEGER) - Current monthly rate
├── daily_price (INTEGER) - Current daily rate
├── price_source (TEXT) - 'site_base' | 'custom' | 'tag'
├── price_source_tag_id (UUID, nullable) - If price from tag
├── manual_status (TEXT, nullable) - 'maintenance' | 'reserved' | NULL
├── notes (TEXT)
├── created_at (TIMESTAMPTZ)
└── updated_at (TIMESTAMPTZ)
```

### Tag Model
```
tags table:
├── id (UUID, primary key)
├── name (TEXT, unique) - e.g., "有屋頂"
├── color (TEXT) - Hex color, e.g., "#2196F3"
├── description (TEXT) - Optional description
├── has_price (BOOLEAN) - Whether tag defines pricing
├── monthly_price (INTEGER, nullable) - Tag monthly rate
├── daily_price (INTEGER, nullable) - Tag daily rate
├── created_at (TIMESTAMPTZ)
└── updated_at (TIMESTAMPTZ)
```

### Space Naming Convention
- Format: `{site_prefix}-{zero_padded_number}` (e.g., A-01, B-15)
- Prefix defined per site, immutable after creation
- Number range: 01-99
- Unique within site (A-01 and B-01 both valid)

### Space Status (4 States)
```
Computed:
  available ← No active agreement covers current_date AND no manual status
  occupied  ← Non-terminated agreement with start_date ≤ today ≤ end_date

Manual (overrides computed):
  maintenance ← Admin-set, blocks new agreements
  reserved    ← Admin-set, blocks new agreements
```

**Priority**: Manual status > Computed availability

### Pricing Hierarchy
```
Priority (highest first):
1. Tag price (if tag has price and was applied to space)
2. Custom price (admin manually set)
3. Site base price (default fallback)
```

See US-SPACE-003 for complete pricing rules.

### Tag System
- Flat list (no categories or hierarchy)
- Multiple tags per space (PostgreSQL TEXT[] array)
- Color per tag for visual indicators
- Optional pricing per tag
- Tag deletion: removes from spaces' arrays, does NOT affect prices
- Tag rename: auto-propagates to all spaces' arrays

## Relationships

**Site → Spaces** (1:N):
- Each space belongs to one site
- Space name includes site prefix
- Deactivating site blocks new agreements on all its spaces

**Tag → Spaces** (M:N via array):
- Tags stored in spaces.tags[] array (NOT junction table)
- Adding tag with price → space price updates
- Removing tag → space price unchanged
- Deleting tag → removed from all spaces' arrays

**Space → Agreements** (1:N, but max 1 active at a time):
- Space can have multiple agreements (historical)
- Only ONE non-terminated agreement can cover any given date
- Agreement overlap check enforced at creation time

**Space → Pricing** (from multiple sources):
- `spaces.monthly_price` / `spaces.daily_price` = current effective price
- `spaces.price_source` tracks where price came from
- Agreement price = immutable snapshot at creation

## UI Pages

Per `09-ui-ux/README.md`:

1. **停車場設定** (`/admin/settings/sites`)
   - Site CRUD with address, prefix, base pricing
   - Deactivation with active agreement check

2. **車位管理 - 列表** (`/admin/spaces`)
   - Table view with filters (site, status, tags)
   - Sort by name, price, status
   - Quick stats summary row
   - Bulk creation support

3. **車位詳情** (`/admin/spaces/:spaceId`)
   - Space info card with pricing source
   - Manual status control (maintenance/reserved)
   - Current agreement section
   - Agreement history table

4. **標籤管理** (`/admin/settings/tags`)
   - Tag CRUD with color and optional pricing
   - Usage count per tag

## Database Schema

```sql
-- Sites
CREATE TABLE sites (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE CHECK (char_length(name) >= 2 AND char_length(name) <= 50),
  prefix TEXT NOT NULL UNIQUE CHECK (char_length(prefix) >= 1 AND char_length(prefix) <= 5),
  address TEXT CHECK (char_length(address) <= 200),
  monthly_base_price INTEGER NOT NULL DEFAULT 3600 CHECK (monthly_base_price >= 0),
  daily_base_price INTEGER NOT NULL DEFAULT 150 CHECK (daily_base_price >= 0),
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Tags
CREATE TABLE tags (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE CHECK (char_length(name) >= 2 AND char_length(name) <= 20),
  color TEXT NOT NULL CHECK (color ~ '^#[0-9A-Fa-f]{6}$'),
  description TEXT CHECK (char_length(description) <= 200),
  has_price BOOLEAN NOT NULL DEFAULT FALSE,
  monthly_price INTEGER CHECK (monthly_price >= 0),
  daily_price INTEGER CHECK (daily_price >= 0),
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  CONSTRAINT check_tag_price CHECK (
    (has_price = TRUE AND monthly_price IS NOT NULL AND daily_price IS NOT NULL)
    OR (has_price = FALSE AND monthly_price IS NULL AND daily_price IS NULL)
  )
);

-- Spaces
CREATE TABLE spaces (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id UUID NOT NULL REFERENCES sites(id),
  name TEXT NOT NULL,
  tags TEXT[] DEFAULT '{}',
  monthly_price INTEGER NOT NULL,
  daily_price INTEGER NOT NULL,
  price_source TEXT NOT NULL DEFAULT 'site_base' CHECK (price_source IN ('site_base', 'custom', 'tag')),
  price_source_tag_id UUID REFERENCES tags(id),
  manual_status TEXT CHECK (manual_status IN ('maintenance', 'reserved')),
  notes TEXT CHECK (char_length(notes) <= 200),
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(site_id, name)
);

CREATE INDEX idx_spaces_site_id ON spaces(site_id);
CREATE INDEX idx_spaces_tags ON spaces USING GIN(tags);
CREATE INDEX idx_spaces_manual_status ON spaces(manual_status);
CREATE INDEX idx_sites_is_active ON sites(is_active);
```

## Audit Logging

All space domain mutations must log to `system_logs`:
- CREATE_SITE / UPDATE_SITE → site changes including base price updates
- CREATE_SPACE / UPDATE_SPACE / DELETE_SPACE → space changes including tag/price updates
- CREATE_TAG / UPDATE_TAG / DELETE_TAG → tag changes

## Test Data

### Sites
| Name | Prefix | Address | Monthly | Daily | Spaces | Status |
|------|--------|---------|---------|-------|--------|--------|
| A區停車場 | A | 屏東市中正路100號 | NT$3,600 | NT$150 | 35 | active |
| B區停車場 | B | 屏東市民生路50號 | NT$4,200 | NT$180 | 40 | active |
| C區停車場 | C | 屏東市復興路200號 | NT$3,000 | NT$120 | 25 | active |

### Tags
| Name | Color | Monthly | Daily | Spaces |
|------|-------|---------|-------|--------|
| 有屋頂 | #2196F3 | NT$4,000 | NT$180 | 12 |
| VIP | #FFD700 | NT$5,000 | NT$220 | 5 |
| 大車位 | #4CAF50 | — | — | 8 |
| 角落位 | #9E9E9E | — | — | 4 |

### Spaces (Sample)
| Name | Site | Tags | Monthly | Daily | Status |
|------|------|------|---------|-------|--------|
| A-01 | A區 | 有屋頂, 大車位 | NT$4,000 | NT$180 | occupied |
| A-02 | A區 | 大車位 | NT$3,600 | NT$150 | available |
| A-03 | A區 | — | NT$3,600 | NT$150 | maintenance |
| B-01 | B區 | VIP, 有屋頂 | NT$5,000 | NT$220 | reserved |

## Dependencies

**Referenced by**:
- US-AGREE-001 (Create Agreement) - selects space, uses space price
- US-AGREE-004 (Double Booking) - checks space availability
- US-AGREE-006 (Agreement Status) - computes space occupancy
- US-PAY-003 (Payment List) - cross-navigation to space

**References**:
- US-LOC-003 (TWD currency format)
- US-LOC-004 (Taiwan date format)
- US-AUDIT-002 (auto-log all actions)

## Future Enhancements (Phase 2/3)

- **Grid view**: Visual grid layout with color-coded space cards (in addition to table view)
- **Space map**: Interactive site map showing physical layout of spaces
- **Occupancy heatmap**: Visual representation of historical occupancy by space
- **Tag categories**: Group tags into categories for better organization
- **Space photos**: Upload photos of individual parking spaces
- **QR codes**: Generate QR codes for each space (for customer self-service)
- **Bulk tag assignment**: Apply tags to multiple spaces at once
- **Space transfer**: Move a space from one site to another
