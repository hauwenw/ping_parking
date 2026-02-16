import pytest
from httpx import AsyncClient


@pytest.fixture
async def payment_setup(auth_client: AsyncClient) -> dict:
    """Create a site, space, customer, agreement, and return IDs."""
    site_resp = await auth_client.post(
        "/api/v1/sites",
        json={"name": "付款測試場", "monthly_base_price": 3600, "daily_base_price": 150},
    )
    space_resp = await auth_client.post(
        "/api/v1/spaces",
        json={"site_id": site_resp.json()["id"], "name": "P-01"},
    )
    customer_resp = await auth_client.post(
        "/api/v1/customers",
        json={"name": "付款客戶", "phone": "0933445566"},
    )
    agreement_resp = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_resp.json()["id"],
            "space_id": space_resp.json()["id"],
            "agreement_type": "monthly",
            "start_date": "2026-03-01",
            "price": 3600,
            "license_plates": "PAY-TEST",
        },
    )
    agreement_id = agreement_resp.json()["id"]

    # Get payment ID
    payment_resp = await auth_client.get(
        f"/api/v1/agreements/{agreement_id}/payment"
    )
    return {
        "agreement_id": agreement_id,
        "payment_id": payment_resp.json()["id"],
        "space_id": space_resp.json()["id"],
    }


@pytest.mark.asyncio
async def test_complete_payment(
    auth_client: AsyncClient, payment_setup: dict
) -> None:
    response = await auth_client.post(
        f"/api/v1/payments/{payment_setup['payment_id']}/complete",
        json={
            "payment_date": "2026-03-01",
            "bank_reference": "TXN-20260301-001",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["bank_reference"] == "TXN-20260301-001"


@pytest.mark.asyncio
async def test_complete_already_completed_fails(
    auth_client: AsyncClient, payment_setup: dict
) -> None:
    await auth_client.post(
        f"/api/v1/payments/{payment_setup['payment_id']}/complete",
        json={
            "payment_date": "2026-03-01",
            "bank_reference": "TXN-001",
        },
    )
    response = await auth_client.post(
        f"/api/v1/payments/{payment_setup['payment_id']}/complete",
        json={
            "payment_date": "2026-03-02",
            "bank_reference": "TXN-002",
        },
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_update_payment_amount(
    auth_client: AsyncClient, payment_setup: dict
) -> None:
    """Update payment amount using new comprehensive endpoint."""
    response = await auth_client.put(
        f"/api/v1/payments/{payment_setup['payment_id']}",
        json={"amount": 3000},
    )
    assert response.status_code == 200
    assert response.json()["amount"] == 3000


@pytest.mark.asyncio
async def test_update_payment_status(
    auth_client: AsyncClient, payment_setup: dict
) -> None:
    """Update payment status from pending to completed."""
    response = await auth_client.put(
        f"/api/v1/payments/{payment_setup['payment_id']}",
        json={"status": "completed"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"


@pytest.mark.asyncio
async def test_update_payment_due_date(
    auth_client: AsyncClient, payment_setup: dict
) -> None:
    """Update payment due_date field."""
    response = await auth_client.put(
        f"/api/v1/payments/{payment_setup['payment_id']}",
        json={"due_date": "2026-03-08"},
    )
    assert response.status_code == 200
    assert response.json()["due_date"] == "2026-03-08"


@pytest.mark.asyncio
async def test_update_completed_payment_allowed(
    auth_client: AsyncClient, payment_setup: dict
) -> None:
    """Completed payments can be edited (spec AC10)."""
    # Complete the payment first
    await auth_client.post(
        f"/api/v1/payments/{payment_setup['payment_id']}/complete",
        json={
            "payment_date": "2026-03-01",
            "bank_reference": "TXN-001",
        },
    )

    # Now edit the completed payment - should succeed
    response = await auth_client.put(
        f"/api/v1/payments/{payment_setup['payment_id']}",
        json={"amount": 2000},
    )
    assert response.status_code == 200
    assert response.json()["amount"] == 2000
    assert response.json()["status"] == "completed"


@pytest.mark.asyncio
async def test_update_multiple_fields(
    auth_client: AsyncClient, payment_setup: dict
) -> None:
    """Update multiple payment fields in single request."""
    response = await auth_client.put(
        f"/api/v1/payments/{payment_setup['payment_id']}",
        json={
            "amount": 2500,
            "status": "completed",
            "payment_date": "2026-03-05",
            "bank_reference": "MULTI-UPDATE-001",
            "notes": "Combined update test",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 2500
    assert data["status"] == "completed"
    assert data["payment_date"] == "2026-03-05"
    assert data["bank_reference"] == "MULTI-UPDATE-001"
    assert data["notes"] == "Combined update test"


@pytest.mark.asyncio
async def test_payment_auto_generation_with_due_date(
    auth_client: AsyncClient
) -> None:
    """Payment auto-generated with due_date = agreement start_date."""
    # Create site, space, customer
    site_resp = await auth_client.post(
        "/api/v1/sites",
        json={"name": "測試場2", "monthly_base_price": 3600, "daily_base_price": 150},
    )
    assert site_resp.status_code == 201
    space_resp = await auth_client.post(
        "/api/v1/spaces",
        json={"site_id": site_resp.json()["id"], "name": "AUTO-01"},
    )
    assert space_resp.status_code == 201
    customer_resp = await auth_client.post(
        "/api/v1/customers",
        json={"name": "自動測試", "phone": "0944556677"},
    )
    assert customer_resp.status_code == 201

    # Create agreement
    agreement_resp = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_resp.json()["id"],
            "space_id": space_resp.json()["id"],
            "agreement_type": "monthly",
            "start_date": "2026-04-15",
            "price": 3600,
            "license_plates": "AUTO-TEST",
        },
    )

    # Check payment was auto-generated with due_date
    payment_resp = await auth_client.get(
        f"/api/v1/agreements/{agreement_resp.json()['id']}/payment"
    )
    data = payment_resp.json()
    assert data["due_date"] == "2026-04-15"  # Should match start_date
    assert data["amount"] == 3600
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_terminated_agreement_voids_payment(
    auth_client: AsyncClient, payment_setup: dict
) -> None:
    await auth_client.post(
        f"/api/v1/agreements/{payment_setup['agreement_id']}/terminate",
        json={"termination_reason": "測試終止"},
    )

    payment_resp = await auth_client.get(
        f"/api/v1/payments/{payment_setup['payment_id']}"
    )
    assert payment_resp.json()["status"] == "voided"
