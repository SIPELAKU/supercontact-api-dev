from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import or_, func
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.user_model import User
from app.schemas import UserGetQuery


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_users(self, query_params: UserGetQuery):
        query = select(User)

        if query_params.search:
            query = query.where(
                or_(
                    User.fullname.ilike(f"%{query_params.search}%"),
                    User.email.ilike(f"%{query_params.search}%"),
                )
            )

        if query_params.role:
            query = query.where(User.role == query_params.role)

        if query_params.status:
            query = query.where(User.status == query_params.status)

        # Count total rows
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar()

        # Pagination
        skip = (query_params.page - 1) * query_params.limit
        result = await self.db.execute(query.offset(skip).limit(query_params.limit))
        users = result.scalars().all()

        return users, total

    async def get_by_email(self, email: EmailStr):
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

    async def get_total(self):
        return await self.db.scalar(select(func.count()).select_from(User))
