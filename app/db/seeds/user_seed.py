import asyncio
from sqlmodel import select

from app.core.security import hash_password
from app.db import get_async_session
from app.models import User, UserPosition


USERS = [
    {
        "fullname": "Super Admin",
        "email": "superadmin@company.com",
        "password": "superadmin",
        "avatar_initial": "SA",
        "phone": "0800000000",
        "company": "PT Supercontact",
        "position": UserPosition.SENIOR_MANAGER,
    },
    {
        "fullname": "Admin",
        "email": "admin@company.com",
        "password": "admin",
        "avatar_initial": "AD",
        "phone": "0811111111",
        "company": "PT Supercontact",
        "position": UserPosition.SENIOR_MANAGER,
    },
    {
        "fullname": "Manager",
        "email": "manager@company.com",
        "password": "manager",
        "avatar_initial": "MG",
        "phone": "0822222222",
        "company": "PT Supercontact",
        "position": UserPosition.SENIOR_MANAGER,
    },
    {
        "fullname": "Staff",
        "email": "staff@company.com",
        "password": "staff",
        "avatar_initial": "ST",
        "phone": "0833333333",
        "company": "PT Supercontact",
        "position": UserPosition.SENIOR_MANAGER,
    },
]


async def seed_users():
    db_gen = get_async_session()
    db = await anext(db_gen)

    try:
        for data in USERS:
            result = await db.execute(select(User).where(User.email == data["email"]))
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print(f"⚠️ User already exists: {data['email']}")
                continue

            user = User(
                fullname=data["fullname"],
                email=data["email"],
                password=hash_password(data["password"]),
                avatar_initial=data["avatar_initial"],
                phone=data["phone"],
                company=data["company"],
                position=data["position"],
            )

            db.add(user)
            print(f"User created: {data['email']}")

        await db.commit()
        print("User seeding completed")

    except Exception as e:
        await db.rollback()
        print("Rollback:", e)

    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(seed_users())
