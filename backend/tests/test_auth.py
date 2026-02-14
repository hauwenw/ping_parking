import pytest
from httpx import AsyncClient

from app.models.admin_user import AdminUser


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, seed_admin: AdminUser) -> None:
    """POST /auth/login with valid credentials returns token."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin1@ping.tw", "password": "Password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user_email"] == "admin1@ping.tw"
    assert data["user_name"] == "管理員一"


@pytest.mark.asyncio
async def test_login_wrong_password(
    client: AsyncClient, seed_admin: AdminUser
) -> None:
    """POST /auth/login with wrong password returns 401."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin1@ping.tw", "password": "WrongPass"},
    )
    assert response.status_code == 401
    assert "電子郵件或密碼錯誤" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_email(client: AsyncClient) -> None:
    """POST /auth/login with unknown email returns 401."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "Password123"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_authenticated(auth_client: AsyncClient) -> None:
    """GET /auth/me with valid token returns user info."""
    response = await auth_client.get("/api/v1/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin1@ping.tw"
    assert data["display_name"] == "管理員一"


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client: AsyncClient) -> None:
    """GET /auth/me without token returns 401."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(auth_client: AsyncClient) -> None:
    """POST /auth/logout with valid token returns success."""
    response = await auth_client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    assert "登出" in response.json()["message"]
