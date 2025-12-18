from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import or_, func
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.user_model import User
from app.schemas import UserGetQuery


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_users(self, query_params: UserGetQuery):
        query = select(User).options(
            selectinload(User.manage_user),
            selectinload(User.detail),
        )

        if query_params.search:
            query = query.where(
                or_(
                    User.fullname.ilike(f"%{query_params.search}%"),
                    User.email.ilike(f"%{query_params.search}%"),
                )
            )

        if query_params.position:
            query = query.where(User.position == query_params.position)

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        skip = (query_params.page - 1) * query_params.limit
        result = await self.db.execute(query.offset(skip).limit(query_params.limit))
        users = result.scalars().all()

        return users, total

    async def get_by_email(self, email: EmailStr):
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.manage_user))
            .where(User.email == email)
        )
        return result.scalars().first()

    async def get_by_id(self, user_id: UUID):
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.manage_user))
            .where(User.id == user_id)
        )
        return result.scalars().first()

    # CREATE
    async def create(self, user: User):
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    # UPDATE
    async def update(self, user: User):
        await self.db.commit()
        await self.db.refresh(user)
        return user

    # DELETE
    async def delete(self, user: User):
        await self.db.delete(user)
        await self.db.commit()

    async def get_all(self):
        result = await self.db.execute(select(User))
        return result.scalars().all()

    async def get_total(self):
        return await self.db.scalar(select(func.count()).select_from(User))
