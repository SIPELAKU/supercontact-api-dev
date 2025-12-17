import asyncio

from sqlalchemy.exc import IntegrityError

from app.db import get_async_session
from app.models import UserRole
from app.models.user_model import RolePermission


async def seed_users():
    db_gen = get_async_session()
    db = await anext(db_gen)

    permission = RolePermission(permission_name="Full Access")
    role = UserRole(role_name="Administrator", permission_id=permission.id)
    db.add(permission)
    db.add(role)
    try:
        await db.commit()
    except IntegrityError:
        print("Rollback")
        await db.rollback()
    finally:
        await db.close()


if __name__ == "__main__":
    print("Running database seed...")
    asyncio.run(seed_users())
    print("Seed completed!")
