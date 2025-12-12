from math import ceil
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.exceptions import AppException
from app.repositories import QuotationRepository
from app.schemas import ErrorCode, QuotationRequest
from app.schemas.quotation_schema import QuotationGetQuery


class QuotationService:
    def __init__(self, db: AsyncSession):
        self.repo = QuotationRepository(db)

    # GET QUOTATION BY ID
    async def find_one_quotation(self, quotation_id: UUID):
        quotation = await self.repo.get_by_id(quotation_id)
        if not quotation:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Quotation not found"
            )
        return quotation

    # CREATE NEW QUOTATION
    async def create_quotation(self, payload: QuotationRequest):
        return await self.repo.create(payload=payload)

    # GET ALL QUOTATIONS
    async def find_all_quotations(self, query_params: QuotationGetQuery):
        quotations, total = await self.repo.get_all(query_params=query_params)
        if not total or not query_params.limit:
            total_pages = 1
            query_params.page = 1
        else:
            total_pages = ceil(total / query_params.limit)

        return {
            "total": total,
            "page": query_params.page,
            "limit": query_params.limit,
            "total_pages": total_pages,
            "quotations": quotations,
        }

    # UPDATE QUOTATION
    async def update_quotation(self, quotation_id: UUID, payload: QuotationRequest):
        quotation = await  self.repo.get_by_id(quotation_id=quotation_id)
        if not quotation:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Quotation not found"
            )

        return await self.repo.update(quotation=quotation, payload=payload)

    # DELETE QUOTATION
    async def delete_quotation(self, quotation_id: UUID):
        quotation = await  self.repo.get_by_id(quotation_id=quotation_id)
        if not quotation:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Quotation not found"
            )

        return await self.repo.delete(quotation=quotation)
