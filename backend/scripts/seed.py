"""Seed script to populate database with demo data for all entities."""

import asyncio
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dateutil.relativedelta import relativedelta
from sqlalchemy import select

from app.database import async_session_factory, engine
from app.models import Base
from app.models.admin_user import AdminUser
from app.models.agreement import Agreement
from app.models.customer import Customer
from app.models.payment import Payment
from app.models.site import Site
from app.models.space import Space
from app.models.tag import Tag
from app.utils.auth import hash_password
from app.utils.crypto import encrypt_license_plate

SEED_USERS = [
    {"email": "admin1@ping.tw", "password": "Password123", "display_name": "管理員一"},
    {"email": "admin2@ping.tw", "password": "Password456", "display_name": "管理員二"},
]

SEED_SITES = [
    {"name": "A場-自由路", "address": "屏東市自由路100號", "description": "主要停車場", "monthly_base_price": 3600, "daily_base_price": 150},
    {"name": "B場-民生路", "address": "屏東市民生路200號", "description": "次要停車場", "monthly_base_price": 3200, "daily_base_price": 130},
    {"name": "C場-復興路", "address": "屏東市復興路50號", "description": "小型停車場", "monthly_base_price": 2800, "daily_base_price": 120},
]

SEED_TAGS = [
    {"name": "有屋頂", "color": "#3B82F6", "description": "有遮蔽停車位"},
    {"name": "VIP", "color": "#EF4444", "description": "VIP專屬車位", "monthly_price": 5000, "daily_price": 200},
    {"name": "大車位", "color": "#F59E0B", "description": "適合大型車輛"},
    {"name": "機車位", "color": "#10B981", "description": "機車專用", "monthly_price": 800, "daily_price": 50},
    {"name": "殘障車位", "color": "#8B5CF6", "description": "無障礙車位"},
]

SEED_CUSTOMERS = [
    {"name": "王大明", "phone": "0912345678", "email": "wang@example.com", "notes": "VIP客戶"},
    {"name": "李小華", "phone": "0923456789", "contact_phone": "0933333333"},
    {"name": "張美玲", "phone": "0934567890", "email": "chang@example.com"},
    {"name": "陳志強", "phone": "0945678901"},
    {"name": "林淑芬", "phone": "0956789012", "notes": "季租客戶"},
    {"name": "黃建國", "phone": "0967890123", "email": "huang@example.com"},
    {"name": "劉美惠", "phone": "0978901234"},
    {"name": "吳俊傑", "phone": "0989012345", "contact_phone": "0911111111"},
]


async def seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        # --- Admin Users ---
        print("Seeding admin users...")
        for user_data in SEED_USERS:
            result = await session.execute(
                select(AdminUser).where(AdminUser.email == user_data["email"])
            )
            if result.scalar_one_or_none():
                print(f"  Skipping {user_data['email']} (exists)")
                continue
            session.add(AdminUser(
                email=user_data["email"],
                hashed_password=hash_password(user_data["password"]),
                display_name=user_data["display_name"],
            ))
            print(f"  Created {user_data['email']}")

        await session.flush()

        # --- Sites ---
        print("Seeding sites...")
        site_objs = {}
        for site_data in SEED_SITES:
            result = await session.execute(
                select(Site).where(Site.name == site_data["name"])
            )
            existing = result.scalar_one_or_none()
            if existing:
                site_objs[site_data["name"]] = existing
                print(f"  Skipping {site_data['name']} (exists)")
                continue
            site = Site(**site_data)
            session.add(site)
            await session.flush()
            site_objs[site_data["name"]] = site
            print(f"  Created {site_data['name']}")

        # --- Tags ---
        print("Seeding tags...")
        for tag_data in SEED_TAGS:
            result = await session.execute(
                select(Tag).where(Tag.name == tag_data["name"])
            )
            if result.scalar_one_or_none():
                print(f"  Skipping tag {tag_data['name']} (exists)")
                continue
            session.add(Tag(**tag_data))
            print(f"  Created tag {tag_data['name']}")

        await session.flush()

        # --- Spaces ---
        print("Seeding spaces...")
        space_configs = [
            # Site A: 40 spaces
            *[{"site": "A場-自由路", "name": f"A-{i:02d}", "tags": ["有屋頂"] if i <= 10 else [], "status": "available"} for i in range(1, 41)],
            # Site B: 35 spaces
            *[{"site": "B場-民生路", "name": f"B-{i:02d}", "tags": ["VIP"] if i <= 5 else (["大車位"] if i <= 10 else []), "status": "available"} for i in range(1, 36)],
            # Site C: 25 spaces
            *[{"site": "C場-復興路", "name": f"C-{i:02d}", "tags": ["機車位"] if i <= 8 else [], "status": "available"} for i in range(1, 26)],
        ]

        space_objs = {}
        for sc in space_configs:
            site = site_objs[sc["site"]]
            result = await session.execute(
                select(Space).where(Space.site_id == site.id, Space.name == sc["name"])
            )
            existing = result.scalar_one_or_none()
            if existing:
                space_objs[sc["name"]] = existing
                continue
            space = Space(
                site_id=site.id,
                name=sc["name"],
                tags=sc["tags"],
                status=sc["status"],
            )
            session.add(space)
            await session.flush()
            space_objs[sc["name"]] = space
        print(f"  Created/verified {len(space_configs)} spaces")

        # --- Customers ---
        print("Seeding customers...")
        cust_objs = {}
        for cust_data in SEED_CUSTOMERS:
            result = await session.execute(
                select(Customer).where(
                    Customer.name == cust_data["name"],
                    Customer.phone == cust_data["phone"],
                )
            )
            existing = result.scalar_one_or_none()
            if existing:
                cust_objs[cust_data["name"]] = existing
                print(f"  Skipping {cust_data['name']} (exists)")
                continue
            cust = Customer(**cust_data)
            session.add(cust)
            await session.flush()
            cust_objs[cust_data["name"]] = cust
            print(f"  Created {cust_data['name']}")

        # --- Agreements + Payments ---
        print("Seeding agreements and payments...")
        today = date.today()
        agreement_configs = [
            {"customer": "王大明", "space": "A-01", "type": "monthly", "start": today - timedelta(days=15), "price": 3600, "plate": "ABC-1234", "paid": True},
            {"customer": "李小華", "space": "A-05", "type": "quarterly", "start": today - timedelta(days=60), "price": 10800, "plate": "DEF-5678", "paid": True},
            {"customer": "張美玲", "space": "B-01", "type": "monthly", "start": today - timedelta(days=5), "price": 5000, "plate": "GHI-9012", "paid": False},
            {"customer": "陳志強", "space": "B-08", "type": "yearly", "start": today - timedelta(days=200), "price": 36000, "plate": "JKL-3456", "paid": True},
            {"customer": "林淑芬", "space": "C-01", "type": "monthly", "start": today - timedelta(days=45), "price": 800, "plate": "MNO-7890", "paid": False},
            {"customer": "黃建國", "space": "A-12", "type": "monthly", "start": today - timedelta(days=10), "price": 3600, "plate": "PQR-1111", "paid": False},
        ]

        for ac in agreement_configs:
            customer = cust_objs.get(ac["customer"])
            space = space_objs.get(ac["space"])
            if not customer or not space:
                print(f"  Skipping agreement for {ac['customer']} (missing ref)")
                continue

            # Check if agreement already exists for this space
            result = await session.execute(
                select(Agreement).where(
                    Agreement.space_id == space.id,
                    Agreement.terminated_at.is_(None),
                )
            )
            if result.scalar_one_or_none():
                print(f"  Skipping {ac['customer']} on {ac['space']} (exists)")
                continue

            end_map = {"daily": relativedelta(days=1), "monthly": relativedelta(months=1), "quarterly": relativedelta(months=3), "yearly": relativedelta(years=1)}
            end_date = ac["start"] + end_map[ac["type"]]

            agreement = Agreement(
                customer_id=customer.id,
                space_id=space.id,
                agreement_type=ac["type"],
                start_date=ac["start"],
                end_date=end_date,
                price=ac["price"],
                license_plates=encrypt_license_plate(ac["plate"]),
            )
            session.add(agreement)
            await session.flush()

            payment = Payment(
                agreement_id=agreement.id,
                amount=ac["price"],
                status="completed" if ac["paid"] else "pending",
                payment_date=ac["start"] if ac["paid"] else None,
                bank_reference=f"REF-{ac['plate'][:3]}" if ac["paid"] else None,
            )
            session.add(payment)

            space.status = "occupied" if end_date >= today else "available"
            print(f"  Created agreement: {ac['customer']} → {ac['space']} ({ac['type']}, {'active' if end_date >= today else 'expired'})")

        await session.commit()
    print("\nSeed complete!")


if __name__ == "__main__":
    asyncio.run(seed())
