"""Tests for three-tier pricing model and space filtering."""

import pytest
from httpx import AsyncClient


@pytest.fixture
async def site_with_pricing(auth_client: AsyncClient) -> str:
    resp = await auth_client.post(
        "/api/v1/sites",
        json={"name": "定價場", "monthly_base_price": 3600, "daily_base_price": 150},
    )
    return resp.json()["id"]


@pytest.fixture
async def tag_with_pricing(auth_client: AsyncClient) -> dict:
    resp = await auth_client.post(
        "/api/v1/tags",
        json={"name": "VIP", "color": "#FF0000", "monthly_price": 5000, "daily_price": 200},
    )
    return resp.json()


@pytest.fixture
async def tag_no_pricing(auth_client: AsyncClient) -> dict:
    resp = await auth_client.post(
        "/api/v1/tags",
        json={"name": "有屋頂", "color": "#00FF00"},
    )
    return resp.json()


@pytest.mark.asyncio
async def test_site_base_pricing(auth_client: AsyncClient, site_with_pricing: str) -> None:
    """Space with no tags or custom price gets site base price."""
    resp = await auth_client.post(
        "/api/v1/spaces",
        json={"site_id": site_with_pricing, "name": "P-01"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["effective_monthly_price"] == 3600
    assert data["effective_daily_price"] == 150
    assert data["price_tier"] == "site"


@pytest.mark.asyncio
async def test_tag_pricing_override(
    auth_client: AsyncClient, site_with_pricing: str, tag_with_pricing: dict
) -> None:
    """Space with a priced tag gets tag pricing."""
    resp = await auth_client.post(
        "/api/v1/spaces",
        json={"site_id": site_with_pricing, "name": "P-02", "tags": ["VIP"]},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["effective_monthly_price"] == 5000
    assert data["effective_daily_price"] == 200
    assert data["price_tier"] == "tag"
    assert data["price_tag_name"] == "VIP"


@pytest.mark.asyncio
async def test_custom_price_override_site(
    auth_client: AsyncClient, site_with_pricing: str
) -> None:
    """Custom price overrides site base pricing (no tags)."""
    resp = await auth_client.post(
        "/api/v1/spaces",
        json={
            "site_id": site_with_pricing,
            "name": "P-03",
            "custom_price": 9999,
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["effective_monthly_price"] == 9999
    assert data["price_tier"] == "custom"


@pytest.mark.asyncio
async def test_custom_price_overrides_tag(
    auth_client: AsyncClient, site_with_pricing: str, tag_with_pricing: dict
) -> None:
    """Custom price has highest priority — overrides tag price."""
    resp = await auth_client.post(
        "/api/v1/spaces",
        json={
            "site_id": site_with_pricing,
            "name": "P-05",
            "tags": ["VIP"],
            "custom_price": 9999,
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    # Custom wins over tag
    assert data["effective_monthly_price"] == 9999
    assert data["price_tier"] == "custom"


@pytest.mark.asyncio
async def test_tag_without_pricing_uses_site(
    auth_client: AsyncClient, site_with_pricing: str, tag_no_pricing: dict
) -> None:
    """Space with a tag that has no pricing falls back to site base price."""
    resp = await auth_client.post(
        "/api/v1/spaces",
        json={"site_id": site_with_pricing, "name": "P-04", "tags": ["有屋頂"]},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["effective_monthly_price"] == 3600
    assert data["price_tier"] == "site"


@pytest.mark.asyncio
async def test_filter_spaces_by_status(auth_client: AsyncClient, site_with_pricing: str) -> None:
    """Filter spaces by status query parameter."""
    await auth_client.post(
        "/api/v1/spaces",
        json={"site_id": site_with_pricing, "name": "F-01"},
    )
    create_resp = await auth_client.post(
        "/api/v1/spaces",
        json={"site_id": site_with_pricing, "name": "F-02"},
    )
    space_id = create_resp.json()["id"]
    await auth_client.put(
        f"/api/v1/spaces/{space_id}",
        json={"status": "maintenance"},
    )

    resp = await auth_client.get("/api/v1/spaces?status=maintenance")
    assert resp.status_code == 200
    data = resp.json()
    assert all(s["status"] == "maintenance" for s in data)
    assert any(s["name"] == "F-02" for s in data)


@pytest.mark.asyncio
async def test_filter_spaces_by_tag(
    auth_client: AsyncClient, site_with_pricing: str, tag_with_pricing: dict
) -> None:
    """Filter spaces by tag query parameter."""
    await auth_client.post(
        "/api/v1/spaces",
        json={"site_id": site_with_pricing, "name": "T-01", "tags": ["VIP"]},
    )
    await auth_client.post(
        "/api/v1/spaces",
        json={"site_id": site_with_pricing, "name": "T-02", "tags": []},
    )

    resp = await auth_client.get("/api/v1/spaces?tag=VIP")
    assert resp.status_code == 200
    data = resp.json()
    assert all("VIP" in s["tags"] for s in data)


@pytest.mark.asyncio
async def test_multiple_priced_tags_first_wins(
    auth_client: AsyncClient, site_with_pricing: str, tag_with_pricing: dict
) -> None:
    """When space has multiple priced tags, the first priced tag wins."""
    # Create a second priced tag
    await auth_client.post(
        "/api/v1/tags",
        json={"name": "Premium", "color": "#0000FF", "monthly_price": 8000, "daily_price": 300},
    )
    # VIP appears first in the tags array → VIP pricing should win
    resp = await auth_client.post(
        "/api/v1/spaces",
        json={"site_id": site_with_pricing, "name": "M-01", "tags": ["VIP", "Premium"]},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["effective_monthly_price"] == 5000
    assert data["effective_daily_price"] == 200
    assert data["price_tier"] == "tag"
    assert data["price_tag_name"] == "VIP"


@pytest.mark.asyncio
async def test_multiple_tags_second_priced_wins(
    auth_client: AsyncClient, site_with_pricing: str, tag_no_pricing: dict, tag_with_pricing: dict
) -> None:
    """When first tag has no price, the second priced tag is used."""
    resp = await auth_client.post(
        "/api/v1/spaces",
        json={"site_id": site_with_pricing, "name": "M-02", "tags": ["有屋頂", "VIP"]},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["effective_monthly_price"] == 5000
    assert data["price_tier"] == "tag"
    assert data["price_tag_name"] == "VIP"
