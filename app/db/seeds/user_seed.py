import asyncio

from sqlalchemy.exc import IntegrityError

from app.core.security import pwd_context
from app.db.session import get_async_session
from app.models.user_model import UserRole, User


async def seed_users():
    db_gen = get_async_session()
    db = await anext(db_gen)
    user_seed = [
        {"fullname": "admin", "email": "admin", "password": pwd_context.hash("admin"), "role": UserRole.ADMIN},
        {"fullname": "admin2", "email": "admin2", "password": pwd_context.hash("admin"), "role": UserRole.SALES},
        {"fullname": "admin3", "email": "admin3", "password": pwd_context.hash("admin"), "role": UserRole.SALES},
        {"fullname": "admin4", "email": "admin4", "password": pwd_context.hash("admin"), "role": UserRole.SALES},
        {"fullname": "admin5", "email": "admin5", "password": pwd_context.hash("admin"), "role": UserRole.SALES},
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
