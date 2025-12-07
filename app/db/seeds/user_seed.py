import asyncio

from sqlalchemy.exc import IntegrityError

from app.core import hash_password
from app.db import get_async_session
from app.models import UserStatus, UserRole, User


async def seed_users():
    db_gen = get_async_session()
    db = await anext(db_gen)
    user_seed = [
        {"fullname": "admin", "email": "admin@test.com", "password": hash_password("admin"), "role": UserRole.ADMIN,
         "status": UserStatus.ACTIVE, "avatar_initial": "AD"},
        {"fullname": "admin2", "email": "admin2@test.com", "password": hash_password("admin"), "role": UserRole.SALES,
         "status": UserStatus.ACTIVE, "avatar_initial": "AD"},
        {"fullname": "admin3", "email": "admin3@test.com", "password": hash_password("admin"), "role": UserRole.SALES,
         "status": UserStatus.ACTIVE, "avatar_initial": "AD"},
        {"fullname": "admin4", "email": "admin4@test.com", "password": hash_password("admin"), "role": UserRole.SALES,
         "status": UserStatus.ACTIVE, "avatar_initial": "AD"},
        {"fullname": "admin5", "email": "admin5@test.com", "password": hash_password("admin"), "role": UserRole.SALES,
         "status": UserStatus.ACTIVE, "avatar_initial": "AD"},
    ]

    for user in user_seed:
        db_user = User(**user)
        db.add(db_user)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
    finally:
        await db.close()


if __name__ == "__main__":
    print("Running database seed...")
    asyncio.run(seed_users())
    print("Seed completed!")
