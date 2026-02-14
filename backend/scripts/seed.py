"""Seed script to create initial admin users."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select

from app.database import async_session_factory, engine
from app.models import Base
from app.models.admin_user import AdminUser
from app.utils.auth import hash_password

SEED_USERS = [
    {
        "email": "admin1@ping.tw",
        "password": "Password123",
        "display_name": "管理員一",
    },
    {
        "email": "admin2@ping.tw",
        "password": "Password456",
        "display_name": "管理員二",
    },
]


async def seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        for user_data in SEED_USERS:
            result = await session.execute(
                select(AdminUser).where(AdminUser.email == user_data["email"])
            )
            existing = result.scalar_one_or_none()
            if existing:
                print(f"  Skipping {user_data['email']} (already exists)")
                continue

            user = AdminUser(
                email=user_data["email"],
                hashed_password=hash_password(user_data["password"]),
                display_name=user_data["display_name"],
            )
            session.add(user)
            print(f"  Created {user_data['email']}")

        await session.commit()
    print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
