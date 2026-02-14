"""Tests for customer search and filtering."""

import pytest
from httpx import AsyncClient


@pytest.fixture
async def customers(auth_client: AsyncClient) -> list[dict]:
    results = []
    for name, phone in [("張大明", "0912345678"), ("李小美", "0923456789"), ("張小明", "0934567890")]:
        resp = await auth_client.post(
            "/api/v1/customers",
            json={"name": name, "phone": phone},
        )
        results.append(resp.json())
    return results


@pytest.mark.asyncio
async def test_search_by_name(auth_client: AsyncClient, customers: list[dict]) -> None:
    resp = await auth_client.get("/api/v1/customers?search=張")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    names = [c["name"] for c in data]
    assert "張大明" in names
    assert "張小明" in names


@pytest.mark.asyncio
async def test_search_by_phone(auth_client: AsyncClient, customers: list[dict]) -> None:
    resp = await auth_client.get("/api/v1/customers?search=0923")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "李小美"


@pytest.mark.asyncio
async def test_search_no_results(auth_client: AsyncClient, customers: list[dict]) -> None:
    resp = await auth_client.get("/api/v1/customers?search=王")
    assert resp.status_code == 200
    assert len(resp.json()) == 0


@pytest.mark.asyncio
async def test_pagination(auth_client: AsyncClient, customers: list[dict]) -> None:
    resp = await auth_client.get("/api/v1/customers?limit=2")
    assert resp.status_code == 200
    assert len(resp.json()) == 2

    resp2 = await auth_client.get("/api/v1/customers?offset=2&limit=2")
    assert resp2.status_code == 200
    assert len(resp2.json()) == 1
