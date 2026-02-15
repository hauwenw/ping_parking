"""Tests for computed space status based on agreements."""

from datetime import date, timedelta

import pytest
from httpx import AsyncClient


@pytest.fixture
async def site_id(auth_client: AsyncClient) -> str:
    resp = await auth_client.post(
        "/api/v1/sites",
        json={"name": "狀態測試場", "monthly_base_price": 3600, "daily_base_price": 150},
    )
    return resp.json()["id"]


@pytest.fixture
async def space_id(auth_client: AsyncClient, site_id: str) -> str:
    resp = await auth_client.post(
        "/api/v1/spaces",
        json={"site_id": site_id, "name": "S-01"},
    )
    return resp.json()["id"]


@pytest.fixture
async def customer_id(auth_client: AsyncClient) -> str:
    resp = await auth_client.post(
        "/api/v1/customers",
        json={"name": "狀態測試客戶", "phone": "0922334455"},
    )
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_future_agreement_space_available(
    auth_client: AsyncClient, customer_id: str, space_id: str
) -> None:
    """Space with future agreement should show as available."""
    # Create future agreement (starts tomorrow)
    tomorrow = date.today() + timedelta(days=1)

    await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": str(tomorrow),
            "price": 3600,
            "license_plates": "FUT-0001",
        },
    )

    # Get space - should still be available
    space_resp = await auth_client.get(f"/api/v1/spaces/{space_id}")
    assert space_resp.status_code == 200
    data = space_resp.json()
    assert data["computed_status"] == "available"
    assert data["active_agreement_id"] is None
    # Stored status field should NOT be mutated
    assert data["status"] == "available"


@pytest.mark.asyncio
async def test_active_agreement_space_occupied(
    auth_client: AsyncClient, customer_id: str, space_id: str
) -> None:
    """Space with active agreement (start_date <= today <= end_date) should show as occupied."""
    # Create agreement that started yesterday
    yesterday = date.today() - timedelta(days=1)

    create_resp = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": str(yesterday),
            "price": 3600,
            "license_plates": "ACT-0001",
        },
    )
    agreement_id = create_resp.json()["id"]

    # Get space - should be occupied
    space_resp = await auth_client.get(f"/api/v1/spaces/{space_id}")
    assert space_resp.status_code == 200
    data = space_resp.json()
    assert data["computed_status"] == "occupied"
    assert data["active_agreement_id"] == agreement_id
    # Stored status field should NOT be mutated
    assert data["status"] == "available"


@pytest.mark.asyncio
async def test_terminated_agreement_space_available(
    auth_client: AsyncClient, customer_id: str, space_id: str
) -> None:
    """Space with terminated agreement should show as available."""
    # Create active agreement
    yesterday = date.today() - timedelta(days=1)

    create_resp = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": str(yesterday),
            "price": 3600,
            "license_plates": "TERM-001",
        },
    )
    agreement_id = create_resp.json()["id"]

    # Terminate the agreement
    await auth_client.post(
        f"/api/v1/agreements/{agreement_id}/terminate",
        json={"termination_reason": "測試終止"},
    )

    # Get space - should be available
    space_resp = await auth_client.get(f"/api/v1/spaces/{space_id}")
    assert space_resp.status_code == 200
    data = space_resp.json()
    assert data["computed_status"] == "available"
    assert data["active_agreement_id"] is None
    # Stored status field should NOT be mutated
    assert data["status"] == "available"


@pytest.mark.asyncio
async def test_expired_agreement_space_available(
    auth_client: AsyncClient, customer_id: str, space_id: str
) -> None:
    """Space with expired agreement (end_date in past) should show as available."""
    # Create agreement that ended yesterday (started 32 days ago, ended yesterday)
    start_date = date.today() - timedelta(days=32)

    await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": str(start_date),
            "price": 3600,
            "license_plates": "EXP-0001",
        },
    )

    # Get space - should be available (agreement expired)
    space_resp = await auth_client.get(f"/api/v1/spaces/{space_id}")
    assert space_resp.status_code == 200
    data = space_resp.json()
    assert data["computed_status"] == "available"
    assert data["active_agreement_id"] is None
    # Stored status field should NOT be mutated
    assert data["status"] == "available"


@pytest.mark.asyncio
async def test_space_list_computed_status(
    auth_client: AsyncClient, customer_id: str, site_id: str
) -> None:
    """Space list endpoint should return computed status for all spaces."""
    # Create 3 spaces
    space1_resp = await auth_client.post(
        "/api/v1/spaces", json={"site_id": site_id, "name": "LIST-01"}
    )
    space2_resp = await auth_client.post(
        "/api/v1/spaces", json={"site_id": site_id, "name": "LIST-02"}
    )
    space3_resp = await auth_client.post(
        "/api/v1/spaces", json={"site_id": site_id, "name": "LIST-03"}
    )

    space1_id = space1_resp.json()["id"]
    space2_id = space2_resp.json()["id"]

    # Create active agreement on space1 only
    yesterday = date.today() - timedelta(days=1)
    await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space1_id,
            "agreement_type": "monthly",
            "start_date": str(yesterday),
            "price": 3600,
            "license_plates": "LST-001",
        },
    )

    # Create future agreement on space2
    tomorrow = date.today() + timedelta(days=1)
    await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space2_id,
            "agreement_type": "monthly",
            "start_date": str(tomorrow),
            "price": 3600,
            "license_plates": "LST-002",
        },
    )

    # List all spaces
    list_resp = await auth_client.get(f"/api/v1/spaces?site_id={site_id}")
    assert list_resp.status_code == 200
    spaces = {s["name"]: s for s in list_resp.json()}

    # LIST-01: active agreement → occupied
    assert spaces["LIST-01"]["computed_status"] == "occupied"
    assert spaces["LIST-01"]["active_agreement_id"] is not None

    # LIST-02: future agreement → available
    assert spaces["LIST-02"]["computed_status"] == "available"
    assert spaces["LIST-02"]["active_agreement_id"] is None

    # LIST-03: no agreement → available
    assert spaces["LIST-03"]["computed_status"] == "available"
    assert spaces["LIST-03"]["active_agreement_id"] is None
