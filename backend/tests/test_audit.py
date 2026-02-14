import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system_log import SystemLog


@pytest.mark.asyncio
async def test_login_creates_audit_log(
    auth_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Successful login should create a LOGIN audit entry."""
    result = await db_session.execute(
        select(SystemLog).where(SystemLog.action == "LOGIN")
    )
    logs = result.scalars().all()
    assert len(logs) >= 1


@pytest.mark.asyncio
async def test_crud_creates_audit_log(
    auth_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Creating a site should produce a CREATE audit entry for 'sites' table."""
    await auth_client.post(
        "/api/v1/sites",
        json={"name": "審計場", "monthly_base_price": 3000, "daily_base_price": 100},
    )

    result = await db_session.execute(
        select(SystemLog).where(
            SystemLog.action == "CREATE",
            SystemLog.table_name == "sites",
        )
    )
    logs = result.scalars().all()
    assert len(logs) >= 1
    log = logs[0]
    assert log.new_values is not None
    assert log.new_values["name"] == "審計場"


@pytest.mark.asyncio
async def test_update_logs_old_and_new_values(
    auth_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Updating a tag should log both old and new values."""
    create_resp = await auth_client.post(
        "/api/v1/tags",
        json={"name": "審計標籤", "color": "#AABBCC"},
    )
    tag_id = create_resp.json()["id"]

    await auth_client.put(
        f"/api/v1/tags/{tag_id}",
        json={"color": "#112233"},
    )

    result = await db_session.execute(
        select(SystemLog).where(
            SystemLog.action == "UPDATE",
            SystemLog.table_name == "tags",
        )
    )
    logs = result.scalars().all()
    assert len(logs) >= 1
    log = logs[0]
    assert log.old_values["color"] == "#AABBCC"
    assert log.new_values["color"] == "#112233"


@pytest.mark.asyncio
async def test_delete_logs_old_values(
    auth_client: AsyncClient, db_session: AsyncSession
) -> None:
    """Deleting a customer should log old values."""
    create_resp = await auth_client.post(
        "/api/v1/customers",
        json={"name": "審計客戶", "phone": "0999888777"},
    )
    customer_id = create_resp.json()["id"]

    await auth_client.delete(f"/api/v1/customers/{customer_id}")

    result = await db_session.execute(
        select(SystemLog).where(
            SystemLog.action == "DELETE",
            SystemLog.table_name == "customers",
        )
    )
    logs = result.scalars().all()
    assert len(logs) >= 1
    assert logs[0].old_values["name"] == "審計客戶"
