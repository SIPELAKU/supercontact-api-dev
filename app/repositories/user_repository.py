from typing import Optional
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, load_leads: bool = False):
        query = select(User)
        if load_leads:
            query = query.options(selectinload(User.leads))
        return await self.db.scalars(query)

    async def get_by_email(self, email: str, load_leads: bool = False) -> Optional[User]:
        query = select(User).where(User.email == email)
        if load_leads:
            query = query.options(selectinload(User.leads))
        return await self.db.scalar(query)

    async def get_by_id(self, user_id: UUID, load_leads: bool = False):
        query = select(User).where(User.id == user_id)
        if load_leads:
            query = query.options(selectinload(User.leads))
        return await self.db.scalar(query)

    async def get_total(self):
        return await self.db.scalar(select(func.count()).select_from(User))
