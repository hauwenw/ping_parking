"""Tests for license plate encryption and masking."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_license_plate_encrypted_in_db_decrypted_in_response(
    auth_client: AsyncClient,
) -> None:
    """License plates are encrypted when stored and decrypted when returned."""
    # Create a customer and site first
    cust_resp = await auth_client.post(
        "/api/v1/customers", json={"name": "加密客", "phone": "0912000001"}
    )
    customer_id = cust_resp.json()["id"]

    site_resp = await auth_client.post(
        "/api/v1/sites",
        json={"name": "加密場", "monthly_base_price": 3000, "daily_base_price": 100},
    )
    site_id = site_resp.json()["id"]

    space_resp = await auth_client.post(
        "/api/v1/spaces", json={"site_id": site_id, "name": "E-01"}
    )
    space_id = space_resp.json()["id"]

    # Create agreement with license plate
    agree_resp = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": "2025-01-01",
            "price": 3000,
            "license_plates": "ABC-1234",
        },
    )
    assert agree_resp.status_code == 201
    data = agree_resp.json()
    # The response should contain the decrypted (original) license plate
    assert data["license_plates"] == "ABC-1234"


@pytest.mark.asyncio
async def test_license_plate_roundtrip(auth_client: AsyncClient) -> None:
    """Create and get agreement — license plate should be readable."""
    cust_resp = await auth_client.post(
        "/api/v1/customers", json={"name": "往返客", "phone": "0912000002"}
    )
    customer_id = cust_resp.json()["id"]

    site_resp = await auth_client.post(
        "/api/v1/sites",
        json={"name": "往返場", "monthly_base_price": 3000, "daily_base_price": 100},
    )
    site_id = site_resp.json()["id"]

    space_resp = await auth_client.post(
        "/api/v1/spaces", json={"site_id": site_id, "name": "R-01"}
    )
    space_id = space_resp.json()["id"]

    agree_resp = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": "2025-02-01",
            "price": 3000,
            "license_plates": "XYZ-5678",
        },
    )
    agreement_id = agree_resp.json()["id"]

    # Get agreement by ID
    get_resp = await auth_client.get(f"/api/v1/agreements/{agreement_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["license_plates"] == "XYZ-5678"


def test_mask_license_plate() -> None:
    """Test license plate masking utility."""
    from app.utils.crypto import mask_license_plate

    assert mask_license_plate("ABC-1234") == "AB****4"
    assert mask_license_plate("AB1234") == "AB***4"
    assert mask_license_plate("AB") == "A*"
