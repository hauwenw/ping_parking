import pytest
from httpx import AsyncClient


@pytest.fixture
async def site_id(auth_client: AsyncClient) -> str:
    resp = await auth_client.post(
        "/api/v1/sites",
        json={"name": "測試場", "monthly_base_price": 3600, "daily_base_price": 150},
    )
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_create_space(auth_client: AsyncClient, site_id: str) -> None:
    response = await auth_client.post(
        "/api/v1/spaces",
        json={"site_id": site_id, "name": "A-01", "tags": ["有屋頂"]},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "A-01"
    assert data["status"] == "available"
    assert data["tags"] == ["有屋頂"]


@pytest.mark.asyncio
async def test_list_spaces_by_site(auth_client: AsyncClient, site_id: str) -> None:
    await auth_client.post(
        "/api/v1/spaces", json={"site_id": site_id, "name": "B-01"}
    )
    await auth_client.post(
        "/api/v1/spaces", json={"site_id": site_id, "name": "B-02"}
    )

    response = await auth_client.get(f"/api/v1/spaces?site_id={site_id}")
    assert response.status_code == 200
    assert len(response.json()) >= 2


@pytest.mark.asyncio
async def test_update_space(auth_client: AsyncClient, site_id: str) -> None:
    create_resp = await auth_client.post(
        "/api/v1/spaces", json={"site_id": site_id, "name": "C-01"}
    )
    space_id = create_resp.json()["id"]

    response = await auth_client.put(
        f"/api/v1/spaces/{space_id}",
        json={"name": "C-01改", "status": "maintenance"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "C-01改"
    assert response.json()["status"] == "maintenance"


@pytest.mark.asyncio
async def test_delete_space(auth_client: AsyncClient, site_id: str) -> None:
    create_resp = await auth_client.post(
        "/api/v1/spaces", json={"site_id": site_id, "name": "D-01"}
    )
    space_id = create_resp.json()["id"]

    response = await auth_client.delete(f"/api/v1/spaces/{space_id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_create_space_invalid_site(auth_client: AsyncClient) -> None:
    response = await auth_client.post(
        "/api/v1/spaces",
        json={"site_id": "00000000-0000-0000-0000-000000000000", "name": "X-01"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_invalid_status_value(auth_client: AsyncClient, site_id: str) -> None:
    create_resp = await auth_client.post(
        "/api/v1/spaces", json={"site_id": site_id, "name": "E-01"}
    )
    space_id = create_resp.json()["id"]

    response = await auth_client.put(
        f"/api/v1/spaces/{space_id}",
        json={"status": "invalid_status"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_duplicate_name_same_site(auth_client: AsyncClient, site_id: str) -> None:
    """Creating a space with a duplicate name in the same site should return 409."""
    await auth_client.post(
        "/api/v1/spaces", json={"site_id": site_id, "name": "DUP-01"}
    )
    response = await auth_client.post(
        "/api/v1/spaces", json={"site_id": site_id, "name": "DUP-01"}
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_same_name_different_site(auth_client: AsyncClient, site_id: str) -> None:
    """Same space name in different sites should be allowed."""
    # Create second site
    site2_resp = await auth_client.post(
        "/api/v1/sites",
        json={"name": "另一場", "monthly_base_price": 3000, "daily_base_price": 120},
    )
    site2_id = site2_resp.json()["id"]

    await auth_client.post(
        "/api/v1/spaces", json={"site_id": site_id, "name": "CROSS-01"}
    )
    response = await auth_client.post(
        "/api/v1/spaces", json={"site_id": site2_id, "name": "CROSS-01"}
    )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_rename_space_to_existing_name(auth_client: AsyncClient, site_id: str) -> None:
    """Renaming a space to an existing name in the same site should return 409."""
    await auth_client.post(
        "/api/v1/spaces", json={"site_id": site_id, "name": "REN-01"}
    )
    create2 = await auth_client.post(
        "/api/v1/spaces", json={"site_id": site_id, "name": "REN-02"}
    )
    space2_id = create2.json()["id"]

    response = await auth_client.put(
        f"/api/v1/spaces/{space2_id}",
        json={"name": "REN-01"},
    )
    assert response.status_code == 409
