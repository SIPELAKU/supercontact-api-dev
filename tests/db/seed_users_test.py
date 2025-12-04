from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import pwd_context
from app.models import User, UserRole


async def seed_users_test(db: AsyncSession):
    user_seeds = [
        {"fullname": "admin", "email": "admin", "password": pwd_context.hash("admin"), "role": UserRole.ADMIN},
        {"fullname": "admin2", "email": "admin2", "password": pwd_context.hash("admin"), "role": UserRole.SALES},
        {"fullname": "admin3", "email": "admin3", "password": pwd_context.hash("admin"), "role": UserRole.SALES},
        {"fullname": "admin4", "email": "admin4", "password": pwd_context.hash("admin"), "role": UserRole.SALES},
        {"fullname": "admin5", "email": "admin5", "password": pwd_context.hash("admin"), "role": UserRole.SALES},
    ]
    for user in user_seeds:
        user = User(**user)
        db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
