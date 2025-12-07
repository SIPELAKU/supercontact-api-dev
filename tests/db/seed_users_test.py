from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import hash_password
from app.models import User, UserRole, UserStatus


async def seed_users_test(db: AsyncSession):
    user = User(
        fullname="admin",
        email="admin@example.com",
        password=hash_password("admin"),
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
        avatar_initial="AD"
    )
    db.add(user)
    try:
        await db.commit()  # wajib commit supaya session aware
        await db.refresh(user)
    except IntegrityError:
        await db.rollback()
