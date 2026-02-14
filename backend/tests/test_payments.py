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
    response = await auth_client.put(
        f"/api/v1/payments/{payment_setup['payment_id']}/amount",
        json={"amount": 3000, "notes": "優惠折扣 NT$600"},
    )
    assert response.status_code == 200
    assert response.json()["amount"] == 3000
    assert response.json()["notes"] == "優惠折扣 NT$600"


@pytest.mark.asyncio
async def test_update_completed_payment_amount_fails(
    auth_client: AsyncClient, payment_setup: dict
) -> None:
    await auth_client.post(
        f"/api/v1/payments/{payment_setup['payment_id']}/complete",
        json={
            "payment_date": "2026-03-01",
            "bank_reference": "TXN-001",
        },
    )
    response = await auth_client.put(
        f"/api/v1/payments/{payment_setup['payment_id']}/amount",
        json={"amount": 2000, "notes": "不應該成功"},
    )
    assert response.status_code == 400


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
