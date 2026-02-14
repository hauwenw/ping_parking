import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_site(auth_client: AsyncClient) -> None:
    response = await auth_client.post(
        "/api/v1/sites",
        json={
            "name": "A場",
            "address": "屏東市自由路100號",
            "monthly_base_price": 3600,
            "daily_base_price": 150,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "A場"
    assert data["monthly_base_price"] == 3600
    assert data["daily_base_price"] == 150
    assert data["space_count"] == 0


@pytest.mark.asyncio
async def test_list_sites(auth_client: AsyncClient) -> None:
    await auth_client.post(
        "/api/v1/sites",
        json={"name": "B場", "monthly_base_price": 3000, "daily_base_price": 120},
    )
    response = await auth_client.get("/api/v1/sites")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(s["name"] == "B場" for s in data)


@pytest.mark.asyncio
async def test_get_site(auth_client: AsyncClient) -> None:
    create_resp = await auth_client.post(
        "/api/v1/sites",
        json={"name": "C場", "monthly_base_price": 2500, "daily_base_price": 100},
    )
    site_id = create_resp.json()["id"]

    response = await auth_client.get(f"/api/v1/sites/{site_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "C場"


@pytest.mark.asyncio
async def test_update_site(auth_client: AsyncClient) -> None:
    create_resp = await auth_client.post(
        "/api/v1/sites",
        json={"name": "D場", "monthly_base_price": 2000, "daily_base_price": 80},
    )
    site_id = create_resp.json()["id"]

    response = await auth_client.put(
        f"/api/v1/sites/{site_id}",
        json={"name": "D場-改", "monthly_base_price": 2200},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "D場-改"
    assert response.json()["monthly_base_price"] == 2200


@pytest.mark.asyncio
async def test_delete_site(auth_client: AsyncClient) -> None:
    create_resp = await auth_client.post(
        "/api/v1/sites",
        json={"name": "E場", "monthly_base_price": 1000, "daily_base_price": 50},
    )
    site_id = create_resp.json()["id"]

    response = await auth_client.delete(f"/api/v1/sites/{site_id}")
    assert response.status_code == 204

    get_resp = await auth_client.get(f"/api/v1/sites/{site_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_create_duplicate_site_name(auth_client: AsyncClient) -> None:
    await auth_client.post(
        "/api/v1/sites",
        json={"name": "重複場", "monthly_base_price": 1000, "daily_base_price": 50},
    )
    response = await auth_client.post(
        "/api/v1/sites",
        json={"name": "重複場", "monthly_base_price": 2000, "daily_base_price": 100},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_delete_site_with_spaces_fails(auth_client: AsyncClient) -> None:
    site_resp = await auth_client.post(
        "/api/v1/sites",
        json={"name": "有車位場", "monthly_base_price": 3000, "daily_base_price": 120},
    )
    site_id = site_resp.json()["id"]

    await auth_client.post(
        "/api/v1/spaces",
        json={"site_id": site_id, "name": "A-01"},
    )

    response = await auth_client.delete(f"/api/v1/sites/{site_id}")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_unauthenticated_access(client: AsyncClient) -> None:
    response = await client.get("/api/v1/sites")
    assert response.status_code == 401
