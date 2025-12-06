from uuid import UUID
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import or_, func

from app.models.user_model import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_users(self, search, role, status, skip, limit):
        query = select(User)

        if search:
            query = query.where(
                or_(
                    User.fullname.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                )
            )

        if role:
            query = query.where(User.role == role)

        if status:
            query = query.where(User.status == status)

        # Count total rows
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar()

        # Pagination
        result = await self.db.execute(query.offset(skip).limit(limit))
        users = result.scalars().all()

        return users, total

    async def get_by_email(self, email: str):
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def get_by_id(self, user_id: UUID):
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def create(self, user: User):
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user: User):
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user: User):
        await self.db.delete(user)
        await self.db.commit()

    async def get_all(self):
        result = await self.db.execute(select(User))
        return result.scalars().all()
