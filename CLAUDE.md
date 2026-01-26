# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Ping Parking Management System - A web-based platform for managing Wu family parking operations in Pingtung City, Taiwan. Manages 3 parking lots with ~100 spaces supporting daily, monthly, quarterly, and yearly rental agreements.

**Tech Stack**: Next.js 14 (TypeScript), Supabase (PostgreSQL), Tailwind CSS + shadcn/ui, Vercel hosting

**Language**: Traditional Chinese (Taiwan) with TWD currency formatting

## Development Commands

### Initial Setup
```bash
npm install
npm run dev              # Start development server at http://localhost:3000
```

### Common Development Tasks
```bash
npm run build           # Production build
npm run lint            # Run ESLint
npm run type-check      # TypeScript type checking
npm test                # Run test suite
npm test -- <file>      # Run single test file
```

### Database Operations
```bash
npx supabase start      # Start local Supabase instance
npx supabase db reset   # Reset database with migrations
npx supabase migration new <name>  # Create new migration
npx supabase db push    # Push migrations to remote
```

## Architecture Overview

### Database Schema (12 Core Tables)

**Primary Entities**:
- `customers` - Customer records with name, phone, email (NO national ID for privacy)
- `spaces` - Parking spaces with site_id, name, tags[] (array), status, custom_price
- `agreements` - Rental contracts linking customer + space + license_plate with agreement_type (daily/monthly/quarterly/yearly)
- `payments` - Payment records linked to agreements with bank references
- `tags` - Flexible tag system with name, color, description (replaces fixed categories)
- `system_logs` - Complete audit trail of all admin actions with old_values/new_values JSON

**Key Relationships**:
- Customer → Agreements (1:N) → Payments (1:1 per agreement)
- Space → Agreement (1:1 when active)
- Tags → Spaces (M:N via array field)

**Important**:
- Each space can have ONLY ONE active agreement at a time
- Spaces use PostgreSQL array type for tags (e.g., `tags: ['有屋頂', 'VIP']`)
- All tables must have Row Level Security (RLS) enabled

### Frontend Structure

**Navigation Hierarchy**:
1. 儀表板 (Dashboard) - Tag stats, occupancy, alerts
2. 停車場管理 (Site Management) - Grid layout showing spaces with color-coded tags
3. 客戶管理 (Customer Management) - Customer list with active agreement counts
4. 合約管理 (Agreement Management) - License plate tracking with cross-page navigation
5. 付款管理 (Payment Management) - Payment history with agreement links
6. 候補名單 (Waiting List) - Manual FIFO queues by site
7. 系統設定 (System Settings) - Tag configuration, admin settings
8. 報表 (Reports) - Occupancy, revenue, late payments

**UI/UX Patterns**:
- Desktop-first responsive design optimized for tablet use
- Cross-page navigation between related entities (customer ↔ agreement ↔ payment)
- Color-coded tag dots on space grids for quick visual scanning
- Modal forms for create/edit operations
- Inline validation with Traditional Chinese error messages

### Tag System Architecture

Tags replace fixed categories with flexible, color-coded labels that support:
- Multiple tags per space (e.g., `['有屋頂', 'VIP', '大車位']`)
- Custom pricing multipliers (Base Price × Tag Multipliers = Final Price)
- Visual indicators via color dots on space grids
- Dynamic filtering and reporting by tag combinations

**Implementation**: Use PostgreSQL array type, NOT junction tables. Query with `@>` operator for tag filtering.

### CSV Import System

Supports 6 bulk import formats with validation:
1. Customers (name, phone, email, notes)
2. Spaces (site, name, tags)
3. Agreements (customer_phone, space_name, license_plate, dates)
4. Payments (agreement_ref, amount, date, bank_ref)
5. Tags (name, color, description)
6. Waiting List (customer_phone, site, priority)

**Workflow**: Template download → validation → progress tracking → import log review → retry failed records

### System Logging Architecture

All admin actions must be logged to `system_logs` with:
- `action` (CREATE/UPDATE/DELETE/IMPORT/etc)
- `table` and `record_id` for traceability
- `old_values` and `new_values` as JSONB for complete audit trail
- `user_id`, `ip_address`, `timestamp`

Implement using Supabase database triggers or middleware, NOT client-side logging.

## Critical Business Rules

### Space Allocation
1. Check space status before allocation
2. Verify no existing active agreement on space
3. Require license plate for ALL agreement types
4. Auto-generate payment record on agreement creation
5. Log all allocation actions to system_logs

### Agreement Lifecycle
- Start date + agreement_type determines end_date automatically
- Status transitions: pending → active → expired/terminated
- Cannot delete agreements with associated payments (soft delete only)
- End date calculation: monthly (+1mo), quarterly (+3mo), yearly (+1yr), daily (+1d)

### Payment Processing
- Payments are recorded manually (no gateway in Phase 1)
- One payment record per agreement (not installments)
- Payment status: pending/completed/refunded
- Payment date may differ from agreement start date
- Bank reference required for audit purposes

### Waiting List Management
- FIFO queue per site (NOT per space)
- Admin manually assigns spaces to waiting list customers
- No automatic allocation
- Remove from list after successful allocation

## Localization Requirements

All UI text, validation messages, and notifications must use Traditional Chinese:
- Phone format: `09XX-XXX-XXX` with validation
- Currency: `NT$1,234` (comma separators)
- Date format: `YYYY年MM月DD日` or ISO for forms
- Number format: Arabic numerals with Chinese units

## Security Considerations

1. **Privacy Compliance**: Never store national ID numbers
2. **RLS Enforcement**: All Supabase tables require Row Level Security policies
3. **Authentication**: Use Supabase Auth with JWT tokens
4. **Audit Trail**: Complete logging for all write operations
5. **License Plate Privacy**: Encrypt in transit, mask in public views

## Testing Strategy

Focus testing on:
- Space allocation conflicts (double-booking prevention)
- Agreement date calculations across all types
- Tag filtering with array operators
- CSV import validation and error handling
- Cross-page navigation data integrity
- RLS policy enforcement

## Common Pitfalls

1. **Do NOT use junction tables for tags** - Use PostgreSQL arrays
2. **Do NOT allow multiple active agreements per space** - Enforce at database level
3. **Do NOT skip system logging** - Required for all mutations
4. **Do NOT hardcode categories** - Everything must use the tag system
5. **Do NOT store sensitive data** - No national IDs, minimize PII

## Deployment Notes

- **Environment**: Vercel (Next.js deployment)
- **Database**: Supabase cloud PostgreSQL
- **Target Cost**: <$50/month (Vercel Pro $20 + SMS $10-30)
- **Monitoring**: Vercel analytics + Supabase dashboard
- **Target Uptime**: 99.9%

## Project Status

Currently in initial planning phase (Week 0). Codebase not yet implemented. Reference `init_draft.md` for complete product specification including timeline, workflows, and UI mockups.
