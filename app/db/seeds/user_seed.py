import asyncio

from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.core import hash_password
from app.db import get_async_session
from app.models import UserStatus, UserRole, User, UserPosition


async def seed_users():
    db_gen = get_async_session()
    db = await anext(db_gen)
    query = await db.scalars(select(UserRole))
    roles = query.all()
    user_seed = [
        {"fullname": "admin", "email": "admin@example.com", "password": hash_password("admin"), "role": roles[0].id,
         "status": UserStatus.ACTIVE, "avatar_initial": "AD", "phone": "123123", "company": "xxxxxx",
         "position": UserPosition.SENIOR_MANAGER},
        {"fullname": "admin2", "email": "admin2@example.com", "password": hash_password("admin"),
         "role": roles[0].id,
         "status": UserStatus.ACTIVE, "avatar_initial": "AD", "phone": "123123", "company": "xxxxxx",
         "position": UserPosition.SENIOR_MANAGER},
        {"fullname": "admin3", "email": "admin3@example.com", "password": hash_password("admin"),
         "role": roles[0].id,
         "status": UserStatus.ACTIVE, "avatar_initial": "AD", "phone": "123123", "company": "xxxxxx",
         "position": UserPosition.SENIOR_MANAGER},
        {"fullname": "admin4", "email": "admin4@example.com", "password": hash_password("admin"),
         "role": roles[0].id,
         "status": UserStatus.ACTIVE, "avatar_initial": "AD", "phone": "123123", "company": "xxxxxx",
         "position": UserPosition.SENIOR_MANAGER},
        {"fullname": "admin5", "email": "admin5@example.com", "password": hash_password("admin"),
         "role": roles[0].id,
         "status": UserStatus.ACTIVE, "avatar_initial": "AD", "phone": "123123", "company": "xxxxxx",
         "position": UserPosition.SENIOR_MANAGER},
    ]

    for user in user_seed:
        db_user = User(**user)
        db.add(db_user)

    try:
        await db.commit()
    except IntegrityError as e:
        print(e)
        print("Rollback")
        await db.rollback()
    finally:
        await db.close()


if __name__ == "__main__":
    print("Running database seed...")
    asyncio.run(seed_users())
    print("Seed completed!")
