import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_customer(auth_client: AsyncClient) -> None:
    response = await auth_client.post(
        "/api/v1/customers",
        json={
            "name": "王大明",
            "phone": "0912345678",
            "email": "wang@example.com",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "王大明"
    assert data["phone"] == "0912345678"
    assert data["active_agreement_count"] == 0


@pytest.mark.asyncio
async def test_list_customers(auth_client: AsyncClient) -> None:
    await auth_client.post(
        "/api/v1/customers",
        json={"name": "李小華", "phone": "0923456789"},
    )
    response = await auth_client.get("/api/v1/customers")
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_get_customer(auth_client: AsyncClient) -> None:
    create_resp = await auth_client.post(
        "/api/v1/customers",
        json={"name": "張三", "phone": "0934567890"},
    )
    customer_id = create_resp.json()["id"]

    response = await auth_client.get(f"/api/v1/customers/{customer_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "張三"


@pytest.mark.asyncio
async def test_update_customer(auth_client: AsyncClient) -> None:
    create_resp = await auth_client.post(
        "/api/v1/customers",
        json={"name": "陳四", "phone": "0945678901"},
    )
    customer_id = create_resp.json()["id"]

    response = await auth_client.put(
        f"/api/v1/customers/{customer_id}",
        json={"email": "chen4@example.com", "notes": "VIP客戶"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "chen4@example.com"
    assert response.json()["notes"] == "VIP客戶"


@pytest.mark.asyncio
async def test_delete_customer(auth_client: AsyncClient) -> None:
    create_resp = await auth_client.post(
        "/api/v1/customers",
        json={"name": "刪除客戶", "phone": "0956789012"},
    )
    customer_id = create_resp.json()["id"]

    response = await auth_client.delete(f"/api/v1/customers/{customer_id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_duplicate_customer(auth_client: AsyncClient) -> None:
    await auth_client.post(
        "/api/v1/customers",
        json={"name": "重複人", "phone": "0967890123"},
    )
    response = await auth_client.post(
        "/api/v1/customers",
        json={"name": "重複人", "phone": "0967890123"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_same_name_different_phone_ok(auth_client: AsyncClient) -> None:
    await auth_client.post(
        "/api/v1/customers",
        json={"name": "同名人", "phone": "0911111111"},
    )
    response = await auth_client.post(
        "/api/v1/customers",
        json={"name": "同名人", "phone": "0922222222"},
    )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_invalid_phone_format(auth_client: AsyncClient) -> None:
    response = await auth_client.post(
        "/api/v1/customers",
        json={"name": "壞電話", "phone": "1234567890"},
    )
    assert response.status_code == 422
