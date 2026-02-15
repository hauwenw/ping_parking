import pytest
from httpx import AsyncClient


@pytest.fixture
async def site_id(auth_client: AsyncClient) -> str:
    resp = await auth_client.post(
        "/api/v1/sites",
        json={"name": "合約測試場", "monthly_base_price": 3600, "daily_base_price": 150},
    )
    return resp.json()["id"]


@pytest.fixture
async def space_id(auth_client: AsyncClient, site_id: str) -> str:
    resp = await auth_client.post(
        "/api/v1/spaces",
        json={"site_id": site_id, "name": "T-01"},
    )
    return resp.json()["id"]


@pytest.fixture
async def customer_id(auth_client: AsyncClient) -> str:
    resp = await auth_client.post(
        "/api/v1/customers",
        json={"name": "合約客戶", "phone": "0911223344"},
    )
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_create_agreement(
    auth_client: AsyncClient, customer_id: str, space_id: str
) -> None:
    response = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": "2026-03-01",
            "price": 3600,
            "license_plates": "ABC-1234",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["agreement_type"] == "monthly"
    assert data["end_date"] == "2026-04-01"
    assert data["price"] == 3600
    assert data["payment_status"] == "pending"
    assert data["customer_name"] == "合約客戶"
    assert data["space_name"] == "T-01"


@pytest.mark.asyncio
async def test_create_agreement_daily(
    auth_client: AsyncClient, customer_id: str, space_id: str
) -> None:
    response = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "daily",
            "start_date": "2026-03-01",
            "price": 150,
            "license_plates": "DEF-5678",
        },
    )
    assert response.status_code == 201
    assert response.json()["end_date"] == "2026-03-02"


@pytest.mark.asyncio
async def test_create_agreement_quarterly(
    auth_client: AsyncClient, customer_id: str, space_id: str
) -> None:
    response = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "quarterly",
            "start_date": "2026-01-15",
            "price": 10000,
            "license_plates": "QRT-0001",
        },
    )
    assert response.status_code == 201
    assert response.json()["end_date"] == "2026-04-15"


@pytest.mark.asyncio
async def test_create_agreement_yearly(
    auth_client: AsyncClient, customer_id: str, space_id: str
) -> None:
    response = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "yearly",
            "start_date": "2026-01-01",
            "price": 40000,
            "license_plates": "YR-0001",
        },
    )
    assert response.status_code == 201
    assert response.json()["end_date"] == "2027-01-01"


@pytest.mark.asyncio
async def test_double_booking_prevented(
    auth_client: AsyncClient, customer_id: str, space_id: str
) -> None:
    # First agreement
    await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": "2026-03-01",
            "price": 3600,
            "license_plates": "ABC-1234",
        },
    )
    # Second agreement on same space
    response = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": "2026-04-01",
            "price": 3600,
            "license_plates": "XYZ-9999",
        },
    )
    assert response.status_code == 400
    assert "DOUBLE_BOOKING" in response.json()["code"]


@pytest.mark.asyncio
async def test_space_status_computed_from_agreement_dates(
    auth_client: AsyncClient, customer_id: str, space_id: str
) -> None:
    """Space status is computed from agreement dates, not stored."""
    await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": "2026-03-01",  # Future agreement
            "price": 3600,
            "license_plates": "ABC-1234",
        },
    )
    space_resp = await auth_client.get(f"/api/v1/spaces/{space_id}")
    data = space_resp.json()
    # Stored status should NOT be mutated
    assert data["status"] == "available"
    # Computed status reflects future agreement (not yet active)
    assert data["computed_status"] == "available"
    assert data["active_agreement_id"] is None


@pytest.mark.asyncio
async def test_terminate_agreement(
    auth_client: AsyncClient, customer_id: str, space_id: str
) -> None:
    create_resp = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": "2026-03-01",
            "price": 3600,
            "license_plates": "ABC-1234",
        },
    )
    agreement_id = create_resp.json()["id"]

    response = await auth_client.post(
        f"/api/v1/agreements/{agreement_id}/terminate",
        json={"termination_reason": "客戶要求提前終止"},
    )
    assert response.status_code == 200
    assert response.json()["terminated_at"] is not None
    assert response.json()["payment_status"] == "voided"

    # Verify space status not mutated, computed status reflects terminated agreement
    space_resp = await auth_client.get(f"/api/v1/spaces/{space_id}")
    data = space_resp.json()
    # Stored status should NOT be mutated
    assert data["status"] == "available"
    # Computed status reflects no active agreement
    assert data["computed_status"] == "available"
    assert data["active_agreement_id"] is None


@pytest.mark.asyncio
async def test_terminate_already_terminated(
    auth_client: AsyncClient, customer_id: str, space_id: str
) -> None:
    create_resp = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": "2026-03-01",
            "price": 3600,
            "license_plates": "ABC-1234",
        },
    )
    agreement_id = create_resp.json()["id"]

    await auth_client.post(
        f"/api/v1/agreements/{agreement_id}/terminate",
        json={"termination_reason": "第一次終止"},
    )
    response = await auth_client.post(
        f"/api/v1/agreements/{agreement_id}/terminate",
        json={"termination_reason": "再次終止"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_list_agreements_by_customer(
    auth_client: AsyncClient, customer_id: str, site_id: str
) -> None:
    # Create two spaces and agreements
    s1 = await auth_client.post(
        "/api/v1/spaces", json={"site_id": site_id, "name": "L-01"}
    )
    s2 = await auth_client.post(
        "/api/v1/spaces", json={"site_id": site_id, "name": "L-02"}
    )

    await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": s1.json()["id"],
            "agreement_type": "monthly",
            "start_date": "2026-03-01",
            "price": 3600,
            "license_plates": "L-001",
        },
    )
    await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": s2.json()["id"],
            "agreement_type": "daily",
            "start_date": "2026-03-01",
            "price": 150,
            "license_plates": "L-002",
        },
    )

    response = await auth_client.get(
        f"/api/v1/agreements?customer_id={customer_id}"
    )
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_get_agreement_payment(
    auth_client: AsyncClient, customer_id: str, space_id: str
) -> None:
    create_resp = await auth_client.post(
        "/api/v1/agreements",
        json={
            "customer_id": customer_id,
            "space_id": space_id,
            "agreement_type": "monthly",
            "start_date": "2026-03-01",
            "price": 3600,
            "license_plates": "PAY-001",
        },
    )
    agreement_id = create_resp.json()["id"]

    response = await auth_client.get(
        f"/api/v1/agreements/{agreement_id}/payment"
    )
    assert response.status_code == 200
    assert response.json()["amount"] == 3600
    assert response.json()["status"] == "pending"
