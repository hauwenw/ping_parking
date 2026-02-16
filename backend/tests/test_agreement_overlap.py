"""Tests for agreement date range overlap validation."""

from datetime import date, timedelta

import pytest
from httpx import AsyncClient


@pytest.fixture
async def site_id(auth_client: AsyncClient) -> str:
    resp = await auth_client.post(
        "/api/v1/sites",
        json={"name": "重疊測試場", "monthly_base_price": 3600, "daily_base_price": 150},
    )
    return resp.json()["id"]


@pytest.fixture
async def space_id(auth_client: AsyncClient, site_id: str) -> str:
    resp = await auth_client.post(
        "/api/v1/spaces",
        json={"site_id": site_id, "name": "OVERLAP-01"},
    )
    return resp.json()["id"]


@pytest.fixture
async def customer_id(auth_client: AsyncClient) -> str:
    resp = await auth_client.post(
        "/api/v1/customers",
        json={"name": "重疊測試客戶", "phone": "0933445566"},
    )
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_future_agreement_on_occupied_space(
    auth_client: AsyncClient, customer_id: str, space_id: str
) -> None:
    """Should allow future agreement on currently occupied space (no overlap)."""
    today = date.today()

    # Create current agreement (today to next month)
    await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": str(today),
            "price": 3600,
            "license_plates": "CUR-0001",
        },
    )

    # Create future agreement (2 months from now)
    future_start = today + timedelta(days=60)
    response = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": str(future_start),
            "price": 3600,
            "license_plates": "FUT-0001",
        },
    )

    # Should succeed - no overlap
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_back_to_back_agreements(
    auth_client: AsyncClient, customer_id: str, space_id: str
) -> None:
    """Should allow back-to-back agreements (one ends when next starts)."""
    start1 = date(2026, 3, 1)

    # First agreement: Mar 1 - Apr 1
    await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": str(start1),
            "price": 3600,
            "license_plates": "B2B-0001",
        },
    )

    # Second agreement: Apr 1 - May 1 (starts when first ends)
    start2 = date(2026, 4, 1)
    response = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": str(start2),
            "price": 3600,
            "license_plates": "B2B-0002",
        },
    )

    # Should succeed - end_date is exclusive
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_contained_agreement_rejected(
    auth_client: AsyncClient, customer_id: str, space_id: str
) -> None:
    """Should reject agreement contained within existing agreement."""
    # Large agreement: Feb 1 - Apr 1
    await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": "2026-02-01",
            "price": 3600,
            "license_plates": "BIG-0001",
        },
    )
    await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": "2026-03-01",
            "price": 3600,
            "license_plates": "BIG-0002",
        },
    )

    # Small agreement contained: Mar 10 - Mar 11 (daily)
    response = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "daily",
            "start_date": "2026-03-10",
            "price": 150,
            "license_plates": "SMALL-001",
        },
    )

    # Should fail - contained within existing
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_multiple_future_agreements_no_overlap(
    auth_client: AsyncClient, customer_id: str, space_id: str
) -> None:
    """Should allow multiple non-overlapping future agreements."""
    # Future agreement 1: April
    response1 = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": "2026-04-01",
            "price": 3600,
            "license_plates": "APR-0001",
        },
    )
    assert response1.status_code == 201

    # Future agreement 2: June (gap in May)
    response2 = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": "2026-06-01",
            "price": 3600,
            "license_plates": "JUN-0001",
        },
    )
    assert response2.status_code == 201

    # Future agreement 3: August
    response3 = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": "2026-08-01",
            "price": 3600,
            "license_plates": "AUG-0001",
        },
    )
    assert response3.status_code == 201


@pytest.mark.asyncio
async def test_terminated_agreement_allows_overlap(
    auth_client: AsyncClient, customer_id: str, space_id: str
) -> None:
    """Terminated agreements should not block overlapping new agreements."""
    # Create agreement and terminate it
    create_resp = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": "2026-03-01",
            "price": 3600,
            "license_plates": "TERM-001",
        },
    )
    agreement_id = create_resp.json()["id"]

    await auth_client.post(
        f"/api/v1/agreements/{agreement_id}/terminate",
        json={"termination_reason": "測試終止"},
    )

    # Create overlapping agreement - should succeed (terminated doesn't count)
    response = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": "2026-03-15",  # Overlaps terminated agreement
            "price": 3600,
            "license_plates": "NEW-0001",
        },
    )

    assert response.status_code == 201
