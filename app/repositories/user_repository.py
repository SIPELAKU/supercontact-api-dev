from typing import List, Optional, Tuple
from uuid import UUID
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.user_model import User, UserStatus


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        query = select(User).where(User.id == user_id)
        result = await self.db.exec(query)
        return result.first()

    async def get_by_email(self, email: str) -> Optional[User]:
        query = select(User).where(func.lower(User.email) == email.lower())
        result = await self.db.exec(query)
        return result.first()

    async def list(
        self,
        search: Optional[str] = None,
        role_id: Optional[UUID] = None,
        status: Optional[UserStatus] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Tuple[List[User], int]:

        query = select(User)

        if search:
            query = query.where(func.lower(User.fullname).like(f"%{search.lower()}%"))

        if role_id:
            query = query.where(User.role_id == role_id)

        if status:
            query = query.where(User.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.exec(count_query)
        total = total.one()

        query = query.offset(offset).limit(limit)
        result = await self.db.exec(query)

        return result.all(), total

    async def update(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        self.db.delete(user)
        await self.db.commit()
