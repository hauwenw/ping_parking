# Customer Management Stories

**Total Stories**: 6 (5 Must Have, 1 Should Have)
**Sprint**: Sprint 2 (Weeks 3-4)

## Must Have Stories

| ID | Story | Priority | Sprint |
|----|-------|----------|--------|
| US-CUST-001 | Create/Register New Customer | Must Have | Sprint 2 |
| US-CUST-002 | View Customer Detail | Must Have | Sprint 2 |
| US-CUST-003 | Edit Customer Information | Must Have | Sprint 2 |
| US-CUST-004 | Search and Filter Customers | Must Have | Sprint 2 |
| US-CUST-005 | Link Customer to Agreement | Must Have | Sprint 2 |

## Overview

Customer management is the foundation for all rental operations. Customers are individuals or companies renting parking spaces. The system stores privacy-compliant customer information without sensitive data like national IDs.

**Key Features**:
- Simple customer registration (name, phone, email, notes)
- Privacy-compliant (no national ID storage per US-SEC-004)
- Active agreement count tracking
- Cross-navigation to agreements
- Search and filter capabilities

**Key Dependencies**: Referenced by Agreement Management, Waiting List

**Estimated Effort**: 8-10 story points

## Critical Business Rules

### Customer Data Model
```
customers table:
├── id (UUID, primary key)
├── name (TEXT, required) - Full name
├── phone (TEXT, required) - Stored without dashes: 09XXXXXXXX (displayed as 09XX-XXX-XXX)
├── contact_phone (TEXT, optional) - Secondary contact phone, same format
├── email (TEXT, optional) - Valid email format
├── notes (TEXT, optional) - Admin notes
├── created_at (TIMESTAMPTZ)
├── updated_at (TIMESTAMPTZ)
├── active_agreement_count (INTEGER, computed) - COUNT of active agreements
└── UNIQUE(name, phone) - Composite unique constraint
```

### Privacy & Data Rules
- **NO National ID**: Must not store Taiwan ID numbers (per US-SEC-004)
- **Name + Phone as Unique Identifier**: The combination of name and phone uniquely identifies a customer. This allows two people sharing the same company phone (different names) to coexist.
- **Contact Phone**: Optional secondary phone field for flexibility when customers change numbers
- **Email Optional**: Not all customers have email
- **No Deletion**: Customer records are never deleted. No delete button in UI. Data preserved for historical reference and audit trail integrity.

### Validation Rules
- **Phone**: Must be 10 digits starting with 09 (stored as `09XXXXXXXX`, displayed as `09XX-XXX-XXX`)
- **Contact Phone**: Same format as phone if provided, no uniqueness constraint
- **Email**: Standard email validation if provided
- **Name**: Required, 2-50 characters
- **Notes**: Optional, max 500 characters

### Uniqueness
- **Name + Phone must be unique** across all customers (composite unique constraint)
- Duplicate name + phone → Error: "此姓名與電話組合已存在"

## Relationships

**Customer → Agreements** (1:N):
- One customer can have multiple agreements (historical + active)
- `agreements.customer_id` → `customers.id`

**Customer → Waiting List** (1:N):
- One customer can be on multiple waiting lists (different sites)
- Should Have feature (Phase 2)

## UI Pages

Per `09-ui-ux/README.md`:

1. **客戶管理 - 列表** (`/admin/customers`)
   - Table view with search/filter
   - Columns: Name, Phone, Email, Active Agreements, Created Date
   - "新增客戶" button → Modal form

2. **客戶詳情** (`/admin/customers/:customerId`)
   - Customer info card
   - Tabs: 基本資料 / 合約記錄 / 候補記錄 (Phase 2)
   - Active agreement count badge
   - "新增合約" button (pre-fills customer)
   - Edit button

## Database Schema

```sql
CREATE TABLE customers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL CHECK (char_length(name) >= 2 AND char_length(name) <= 50),
  phone TEXT NOT NULL CHECK (phone ~ '^09[0-9]{8}$'),
  contact_phone TEXT CHECK (contact_phone ~ '^09[0-9]{8}$'),
  email TEXT CHECK (email ~ '^[^@]+@[^@]+\.[^@]+$'),
  notes TEXT CHECK (char_length(notes) <= 500),
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Computed field via join (not stored)
-- active_agreement_count = COUNT of agreements where status='active'

ALTER TABLE customers ADD CONSTRAINT uq_customers_name_phone UNIQUE (name, phone);

CREATE INDEX idx_customers_phone ON customers(phone);
CREATE INDEX idx_customers_name ON customers(name);
CREATE INDEX idx_customers_created_at ON customers(created_at DESC);
```

## Audit Logging

All customer mutations must log to `system_logs`:
- CREATE customer → `action='CREATE_CUSTOMER'`, `old_values=null`, `new_values={...}`
- UPDATE customer → `action='UPDATE_CUSTOMER'`, `old_values={...}`, `new_values={...}`
- No DELETE action — customer records are never deleted

## Test Data

```json
[
  {
    "id": "cust-001",
    "name": "王小明",
    "phone": "0912345678",
    "contact_phone": null,
    "email": "wang@example.com",
    "notes": "VIP客戶，需要有屋頂的車位",
    "active_agreement_count": 2
  },
  {
    "id": "cust-002",
    "name": "李小華",
    "phone": "0923456789",
    "contact_phone": "0933111222",
    "email": null,
    "notes": "",
    "active_agreement_count": 0
  },
  {
    "id": "cust-003",
    "name": "陳大同",
    "phone": "0934567890",
    "contact_phone": null,
    "email": "chen@company.com.tw",
    "notes": "公司戶，需要發票",
    "active_agreement_count": 1
  }
]
```

## Dependencies

**Referenced by**:
- US-AGREE-001 (Create Agreement) - requires customer selection
- US-AGREE-005 (View Agreement Detail) - displays customer name link
- US-AGREE-008 (Cross-Page Navigation) - customer detail → agreements
- US-WAIT-001 (Add to Waiting List) - requires customer (Phase 2)

**References**:
- US-LOC-001 (Traditional Chinese UI) - all labels
- US-LOC-002 (Taiwan Phone Format) - phone validation
- US-AUDIT-002 (Auto-Log Actions) - mutation logging
- US-SEC-004 (Privacy-Compliant Data) - no national ID
- US-UI-003 (Customer List Page) - to be written
- US-UI-004 (Customer Detail Page) - to be written

## Future Enhancements (Phase 2/3)

- **Customer archive/hide**: Allow admin to hide inactive customers from default list view (data preserved)
- **Customer import**: Bulk CSV import (US-BULK-002)
- **Customer export**: Export customer list with filters
- **Communication history**: Track SMS/email sent to customers
- **Customer tags**: Categorize customers (VIP, company, individual)
- **Duplicate detection**: Warn when creating similar customer (fuzzy name match)
