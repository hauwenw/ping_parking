import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_tag(auth_client: AsyncClient) -> None:
    response = await auth_client.post(
        "/api/v1/tags",
        json={"name": "有屋頂", "color": "#FF5733", "monthly_price": 4000},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "有屋頂"
    assert data["color"] == "#FF5733"
    assert data["monthly_price"] == 4000


@pytest.mark.asyncio
async def test_list_tags(auth_client: AsyncClient) -> None:
    await auth_client.post(
        "/api/v1/tags",
        json={"name": "VIP", "color": "#00FF00"},
    )
    response = await auth_client.get("/api/v1/tags")
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_update_tag(auth_client: AsyncClient) -> None:
    create_resp = await auth_client.post(
        "/api/v1/tags",
        json={"name": "大車位", "color": "#0000FF"},
    )
    tag_id = create_resp.json()["id"]

    response = await auth_client.put(
        f"/api/v1/tags/{tag_id}",
        json={"color": "#FF0000", "monthly_price": 5000},
    )
    assert response.status_code == 200
    assert response.json()["color"] == "#FF0000"
    assert response.json()["monthly_price"] == 5000


@pytest.mark.asyncio
async def test_delete_tag(auth_client: AsyncClient) -> None:
    create_resp = await auth_client.post(
        "/api/v1/tags",
        json={"name": "刪除測試", "color": "#AAAAAA"},
    )
    tag_id = create_resp.json()["id"]

    response = await auth_client.delete(f"/api/v1/tags/{tag_id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_duplicate_tag_name(auth_client: AsyncClient) -> None:
    await auth_client.post(
        "/api/v1/tags",
        json={"name": "重複標籤", "color": "#111111"},
    )
    response = await auth_client.post(
        "/api/v1/tags",
        json={"name": "重複標籤", "color": "#222222"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_invalid_color_format(auth_client: AsyncClient) -> None:
    response = await auth_client.post(
        "/api/v1/tags",
        json={"name": "壞顏色", "color": "red"},
    )
    assert response.status_code == 422
