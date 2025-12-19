from uuid import UUID

from sqlmodel import select, func, asc, desc
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.mailing_model import Mailing


class MailingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, mailing: Mailing):
        self.db.add(mailing)
        await self.db.commit()
        await self.db.refresh(mailing)
        return mailing

    async def get_by_id(self, user_id: UUID, mailing_id: UUID):
        query = (
            select(Mailing)
            .where(
                Mailing.id == mailing_id,
                Mailing.user_id == user_id
            )
        )
        return await self.db.scalar(query)

    async def get_all(self, user_id: UUID, query):
        q = select(Mailing).where(Mailing.user_id == user_id)

        if query.search:
            like = f"%{query.search}%"
            q = q.where(
                Mailing.subject.ilike(like)
            )

        total = await self.db.scalar(
            select(func.count(Mailing.id)).where(Mailing.user_id == user_id)
        )

        offset = (query.page - 1) * query.limit

        result = await self.db.scalars(
            q.offset(offset).limit(query.limit)
        )
        return result.all(), total

    async def update(self, mailing: Mailing, payload):
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(mailing, key, value)

        await self.db.commit()
        await self.db.refresh(mailing)
        return mailing

    async def delete(self, mailing: Mailing):
        await self.db.delete(mailing)
        await self.db.commit()
        return True
