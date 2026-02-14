"""Three-tier pricing model for parking spaces.

Priority: Tag price > Custom space price > Site base price
(Per US-SPACE-003 spec)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.site import Site
    from app.models.tag import Tag


def compute_space_price(
    site: Site,
    tags: list[str],
    all_tags: list[Tag],
    custom_price: int | None,
) -> dict:
    """Compute the effective price for a space.

    Priority: Tag price > Custom price > Site base price.
    Returns dict with keys: monthly, daily, tier, tag_name (if tag-priced).
    """
    site_monthly = site.monthly_base_price or 0
    site_daily = site.daily_base_price or 0

    # Start with site base price
    monthly = site_monthly
    daily = site_daily
    tier = "site"
    tag_name = None

    # Custom price overrides site base
    if custom_price is not None:
        monthly = custom_price
        tier = "custom"

    # Tag price has highest priority — overrides both site and custom
    if tags:
        tag_map = {t.name: t for t in all_tags}
        for tag_str in tags:
            tag = tag_map.get(tag_str)
            if tag and (tag.monthly_price is not None or tag.daily_price is not None):
                if tag.monthly_price is not None:
                    monthly = tag.monthly_price
                if tag.daily_price is not None:
                    daily = tag.daily_price
                tier = "tag"
                tag_name = tag.name
                break

    return {
        "monthly": monthly,
        "daily": daily,
        "tier": tier,
        "tag_name": tag_name,
        "site_monthly": site_monthly,
        "site_daily": site_daily,
    }
