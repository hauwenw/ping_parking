# US-SPACE-003: Space Pricing Model (Base + Tag + Custom Override)

**Priority**: Must Have | **Phase**: Phase 1 | **Sprint**: Sprint 2 (Weeks 3-4)
**Domain**: Space Management | **Epic**: Space Configuration

## User Story
As a parking lot admin, I want to set pricing at site level with optional per-space custom pricing and tag-based price adjustments, so that I can flexibly manage rates while minimizing manual updates across similar spaces.

## Acceptance Criteria

### Base Pricing
- **AC1**: Each site has default monthly and daily base prices (e.g., Site A: monthly=NT$3,600, daily=NT$150)
- **AC2**: When creating a new space, it inherits the site's base prices by default
- **AC3**: Admin can override space price manually (custom price per space), which breaks inheritance from site base price

### Tag-Based Pricing
- **AC4**: Each tag can optionally define monthly and daily price adjustments (e.g., "有屋頂" tag: monthly=NT$4,000, daily=NT$180)
- **AC5**: When a tag with price is added to a space → Space price updates to tag's price immediately
- **AC6**: When a tag with price is removed from a space → Space price remains unchanged (does not revert to site base)
- **AC7**: If a space has multiple tags with prices → Last applied tag's price wins (most recent tag assignment)
- **AC8**: Tags without price settings → No effect on space price

### Price Display & Calculation
- **AC9**: Space list and detail pages display: Monthly price, Daily price, Price source indicator ("站點預設" / "自訂價格" / "標籤: 有屋頂")
- **AC10**: Agreement creation form auto-fills price based on:
  - Agreement type: monthly → use space monthly price
  - Agreement type: daily → use space daily price × duration in days
  - Agreement type: quarterly → use space monthly price × 3
  - Agreement type: yearly → use space monthly price × 12
- **AC11**: Admin can manually edit the calculated price on agreement form before saving
- **AC12**: After agreement is created, its price is immutable (stored snapshot) — space/tag price changes do NOT affect existing agreements

### Price Change Impact
- **AC13**: Changing site base price → Updates all spaces using site default (not custom-priced spaces)
- **AC14**: Changing tag price → Does NOT auto-update spaces already tagged (manual re-tag required to apply new price)
- **AC15**: All price changes logged to `system_logs` with old/new values

## Business Rules

### Pricing Hierarchy
1. **Custom space price** (if admin manually set price for this space) — HIGHEST PRIORITY
2. **Tag price** (if tag has price defined and was applied to space)
3. **Site base price** (default fallback)

**Priority**: Custom price > Tag price > Site base price

**Rationale**: Custom price represents an explicit manual override by the admin and should take precedence over all automatic pricing (tag or site base). This ensures that when an admin sets a custom price, it truly overrides everything.

### Price Inheritance & Overrides
- **Site base → Space**: Automatic inheritance on space creation, updates when site base changes (unless custom override or tag price exists)
- **Tag price → Space**: Applies when tag with price is added (overrides site base, but NOT custom price)
- **Custom price**: Admin can always manually set custom price, which has HIGHEST priority and overrides both tag and site base prices

### Price Immutability for Agreements
- Agreement price = snapshot of space price at creation time
- Stored in `agreements.price` field
- Never auto-updates, even if space/tag/site prices change later
- Admin can manually edit agreement price via edit form (logged to audit)

### Tag Price Behavior
- **Add tag with price**: Space price updates immediately ONLY if custom_price is NULL (custom price has higher priority)
- **Remove tag**: Price stays (does NOT revert to previous source), price_source changes to 'custom'
- **Multiple tags with prices**: Last applied tag wins (if no custom price set)
- **Update tag price definition**: Does NOT auto-update spaces (prevents unexpected bulk changes)
- **Tag price vs Custom price**: If space has custom_price set, adding a tag with price does NOT override the custom price

## UI Requirements

### Site Settings Page
**Location**: `/admin/settings/sites/:siteId`
- **Fields**:
  - 月租基本價格 (Monthly base price): NT$ input, required
  - 日租基本價格 (Daily base price): NT$ input, required
- **Save**: Updates site base price, shows spaces affected count, logs change

### Space Detail/Edit
**Location**: `/admin/spaces/:spaceId` or edit modal
- **Price Display**:
  ```
  月租價格: NT$4,000 (標籤: 有屋頂)
  日租價格: NT$180 (標籤: 有屋頂)
  ```
  - Source indicator: 站點預設 / 自訂價格 / 標籤: [tag_name]
- **Custom Price Override**:
  - Checkbox: "自訂此車位價格" (unchecked by default)
  - If checked → Show editable price inputs, breaks inheritance
  - If unchecked → Show read-only price from tag or site base

### Tag Settings Page
**Location**: `/admin/settings/tags/:tagId`
- **Optional Price Fields**:
  - Checkbox: "此標籤設定價格" (unchecked by default)
  - If checked → Show monthly price & daily price inputs
  - If unchecked → Tag does not affect space pricing
- **Warning on save**: "此標籤目前已應用於 X 個車位，價格變更不會自動更新現有車位。如需更新價格，請移除後重新加入標籤。"

### Agreement Creation Form
**Location**: `/admin/agreements/new`
- **Price Calculation**:
  - Auto-fills based on space price + agreement type
  - Formula displayed: "月租價格 NT$4,000 × 3 個月 = NT$12,000"
- **Manual Override**:
  - Price field is editable (yellow highlight when manually changed)
  - Info text: "價格已自動計算，您可手動調整"
- **Price Source Display**: "基於車位 A-01 當前價格 (標籤: 有屋頂)"

## Implementation Notes

### Database Schema

**Sites table** (add pricing columns):
```sql
ALTER TABLE sites ADD COLUMN monthly_base_price INTEGER NOT NULL DEFAULT 3600;
ALTER TABLE sites ADD COLUMN daily_base_price INTEGER NOT NULL DEFAULT 150;
```

**Spaces table** (add pricing columns):
```sql
ALTER TABLE spaces ADD COLUMN custom_price INTEGER; -- NULL means no override; when set, has HIGHEST priority
ALTER TABLE spaces ADD COLUMN monthly_price INTEGER NOT NULL; -- Computed effective price
ALTER TABLE spaces ADD COLUMN daily_price INTEGER NOT NULL;
ALTER TABLE spaces ADD COLUMN price_source TEXT CHECK (price_source IN ('site_base', 'custom', 'tag'));
ALTER TABLE spaces ADD COLUMN price_source_tag_id UUID REFERENCES tags(id); -- NULL if not from tag

-- Note: custom_price only sets monthly price; daily price follows tag or site base
```

**Tags table** (add optional pricing):
```sql
ALTER TABLE tags ADD COLUMN has_price BOOLEAN DEFAULT FALSE;
ALTER TABLE tags ADD COLUMN monthly_price INTEGER;
ALTER TABLE tags ADD COLUMN daily_price INTEGER;
ALTER TABLE tags ADD CONSTRAINT check_tag_price
  CHECK ((has_price = TRUE AND monthly_price IS NOT NULL AND daily_price IS NOT NULL)
      OR (has_price = FALSE AND monthly_price IS NULL AND daily_price IS NULL));
```

**Agreements table** (price snapshot):
```sql
-- Price field already exists in agreement schema
-- No change needed, just confirm it's INTEGER storing the final amount
```

### Price Calculation Logic

**Space price on creation**:
```typescript
function getInitialSpacePrice(siteId: string): { monthly: number, daily: number } {
  const site = await getSite(siteId);
  return {
    monthly: site.monthly_base_price,
    daily: site.daily_base_price,
    price_source: 'site_base'
  };
}
```

**Space price after tag added**:
```typescript
function applyTagToSpace(spaceId: string, tagId: string) {
  const space = await getSpace(spaceId);
  const tag = await getTag(tagId);

  // Only apply tag price if space doesn't have custom price
  if (tag.has_price && space.custom_price === null) {
    await updateSpace(spaceId, {
      monthly_price: tag.monthly_price,
      daily_price: tag.daily_price,
      price_source: 'tag',
      price_source_tag_id: tagId
    });
  }
  // If space has custom price or tag has no price, only update tags array
}
```

**Agreement price calculation**:
```typescript
function calculateAgreementPrice(spaceId: string, agreementType: string): number {
  const space = await getSpace(spaceId);

  switch (agreementType) {
    case 'daily':
      return space.daily_price; // × duration handled separately
    case 'monthly':
      return space.monthly_price;
    case 'quarterly':
      return space.monthly_price * 3;
    case 'yearly':
      return space.monthly_price * 12;
  }
}
```

## Source
CLAUDE.md (tag-based pricing), init_draft.md (space pricing)

## Dependencies
- US-SPACE-001 (site configuration — base prices defined here)
- US-SPACE-002 (space management — price inheritance on creation)
- US-SPACE-004 (tag management — tag pricing integration)
- US-AGREE-001 (create agreement — price snapshot)
- US-LOC-003 (TWD currency format)
- US-AUDIT-002 (audit logging)

## Test Data

### Site Base Pricing
**Site A**:
- Monthly base: NT$3,600
- Daily base: NT$150

**Site B**:
- Monthly base: NT$4,200
- Daily base: NT$180

### Tag Pricing
**Tag "有屋頂"** (has_price=true):
- Monthly: NT$4,000
- Daily: NT$180

**Tag "VIP"** (has_price=true):
- Monthly: NT$5,000
- Daily: NT$220

**Tag "大車位"** (has_price=false):
- No price impact

### Space Pricing Examples

**Space A-01** (inherits site base):
- Site A base: monthly=3600, daily=150
- Tags: ['大車位'] (no price)
- Price: monthly=3600, daily=150, source='site_base'

**Space A-02** (tag price):
- Site A base: monthly=3600
- Tags: ['有屋頂'] (monthly=4000, daily=180)
- Price: monthly=4000, daily=180, source='tag', source_tag_id=tag-001

**Space A-03** (custom price):
- Site A base: monthly=3600
- Admin sets custom: monthly=3800, daily=160
- Tags: [] (no tags)
- Price: monthly=3800, daily=160, source='custom'

**Space A-04** (tag removed, price kept):
1. Initial: Tags=[], monthly=3600 (site base)
2. Add "有屋頂" tag → monthly=4000 (tag price)
3. Remove "有屋頂" tag → monthly=4000 (price unchanged), source='custom'

**Space A-05** (multiple tags with prices):
1. Add "有屋頂" tag (monthly=4000) → Price=4000, source='tag'
2. Add "VIP" tag (monthly=5000) → Price=5000, source='tag' (last tag wins)

**Space A-06** (custom price overrides tag price):
1. Initial: Tags=[], monthly=3600 (site base)
2. Admin sets custom_price=3800 → monthly=3800, source='custom'
3. Add "有屋頂" tag (monthly=4000) → Price stays 3800 (custom overrides tag), source='custom'
4. Remove custom_price (set to null) → Price updates to 4000 (tag price now applies), source='tag'

### Agreement Price Calculation

**Monthly agreement** (Space A-02, monthly=4000):
- Type: monthly
- Calculated price: NT$4,000
- Admin can edit before save

**Daily agreement** (Space A-02, daily=180, 5 days):
- Type: daily, duration: 5 days
- Calculated price: NT$180 × 5 = NT$900

**Quarterly agreement** (Space A-02, monthly=4000):
- Type: quarterly
- Calculated price: NT$4,000 × 3 = NT$12,000

**Yearly agreement** (Space A-02, monthly=4000):
- Type: yearly
- Calculated price: NT$4,000 × 12 = NT$48,000

### Price Change Scenarios

**Scenario 1: Site base price increases**:
1. Site A base changes: 3600 → 4000
2. Space A-01 (site_base, no custom, no tags) → Auto-updates to 4000
3. Space A-02 (tag, no custom) → No change (still 4000 from tag)
4. Space A-03 (custom) → No change (still 3800, custom has highest priority)

**Scenario 2: Tag price changes**:
1. "有屋頂" tag price changes: 4000 → 4500
2. Space A-02 (currently tagged) → No auto-update (still 4000)
3. Admin must remove & re-add tag to apply new price

**Scenario 3: Agreement created, then space price changes**:
1. Create agreement for Space A-02 (monthly=4000) → Agreement price=4000
2. Later, Space A-02 price changes to 4500 (new tag applied or custom price set)
3. Existing agreement price → Still 4000 (immutable snapshot)
4. New agreements for A-02 → Use 4500

**Scenario 4: Custom price priority**:
1. Space A-07 has tag "有屋頂" (monthly=4000) → Price=4000, source='tag'
2. Admin sets custom_price=4200 → Price=4200, source='custom'
3. Later, admin adds "VIP" tag (monthly=5000) → Price stays 4200 (custom overrides tag)
4. Admin removes custom_price (sets to null) → Price updates to 5000 (VIP tag price now applies)
