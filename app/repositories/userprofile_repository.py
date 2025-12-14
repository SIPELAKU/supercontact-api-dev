from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import Optional
from uuid import UUID

from app.models.user_model import User
from app.models.userprofile_model import UserDetail


class UserProfileRepository:
    async def get_user(self, db: AsyncSession, user_id: UUID) -> Optional[User]:
        q = select(User).where(User.id == user_id)
        r = await db.execute(q)
        return r.scalars().first()

    async def get_user_detail(self, db: AsyncSession, user_id: UUID) -> Optional[UserDetail]:
        q = select(UserDetail).where(UserDetail.user_id == user_id)
        r = await db.execute(q)
        return r.scalar_one_or_none()

    async def upsert_user_detail(self, db: AsyncSession, user_id: UUID, data: dict) -> UserDetail:
        detail = await self.get_user_detail(db, user_id)
        if not detail:
            detail = UserDetail(user_id=user_id, **data)
            db.add(detail)
            await db.commit()
            await db.refresh(detail)
            return detail
        for k, v in data.items():
            setattr(detail, k, v)
            db.add(detail)
            await db.commit()
            await db.refresh(detail)
            return detail