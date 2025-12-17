from math import ceil
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.app_exception import AppException, ErrorCode
from app.models.mailing_model import Mailing
from app.repositories.mailing_repository import MailingRepository
from app.schemas.mailing_schema import (
    MailingCreate, MailingUpdate
)


class MailingService:
    def __init__(self, db: AsyncSession):
        self.repo = MailingRepository(db)

    async def create_mailing(self, user_id: UUID, data: MailingCreate):
        mailing = await self.repo.create(Mailing(user_id=user_id, **data.model_dump()))
        return mailing

    async def find_all_mailings(self, user_id: UUID, query):
        mailings, total = await self.repo.get_all(user_id=user_id, query=query)
        total_pages = ceil(total / query.limit) if total else 1

        return {
            "total": total,
            "page": query.page,
            "limit": query.limit,
            "total_pages": total_pages,
            "data": mailings
        }

    async def find_one_mailing(self, user_id: UUID, mailing_id: UUID):
        mailing = await self.repo.get_by_id(user_id=user_id, mailing_id=mailing_id)
        if not mailing:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Mailing not found"
            )
        return mailing

    async def update_mailing(self, user_id: UUID, mailing_id: UUID, data: MailingUpdate):
        mailing = await self.repo.get_by_id(user_id=user_id, mailing_id=mailing_id)
        if not mailing:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Mailing not found"
            )
        return await self.repo.update(mailing, data)

    async def delete_mailing(self, user_id: UUID, mailing_id: UUID):
        mailing = await self.repo.get_by_id(user_id=user_id, mailing_id=mailing_id)
        if not mailing:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Mailing not found"
            )
        return await self.repo.delete(mailing)
