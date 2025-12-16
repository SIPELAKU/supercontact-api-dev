from math import ceil
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.exceptions.app_exception import AppException
from app.repositories import LeadRepository
from app.schemas import ErrorCode, LeadRequest, LeadGetQuery, LeadUpdateStatus


class LeadService:
    def __init__(self, db: AsyncSession):
        self.repo = LeadRepository(db)

    # CREATE NEW LEAD
    async def create_lead(self, payload: LeadRequest):
        # FIND USER FOR ASSIGNED_TO
        user = await self.repo.get_by_assigned_to(payload.assigned_to)
        if not user:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="User not found"
            )

        return await self.repo.create(payload=payload, load_user=True, load_contact=True)

    # FIND ALL LEADS
    async def find_all_leads(self, query_params: LeadGetQuery):
        leads, total = await self.repo.get_all(query_params=query_params, load_user=True, load_contact=True)
        total_pages = ceil(total / query_params.limit) if total else 1

        return {
            "total": total,
            "page": query_params.page,
            "limit": query_params.limit,
            "total_pages": total_pages,
            "leads": leads,
        }

    # FIND LEAD BY ID
    async def find_one_lead(self, lead_id: UUID):
        lead = await self.repo.get_by_id(lead_id=lead_id, load_user=True, load_contact=True)
        if not lead:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Lead not found"
            )
        return lead

    # UPDATE LEAD BY ID
    async def update_lead(self, lead_id: UUID, payload: LeadRequest):
        lead = await self.repo.get_by_id(lead_id=lead_id)
        if not lead:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Lead not found"
            )

        return await self.repo.update(lead=lead, payload=payload, load_user=True, load_contact=True)

    # UPDATE LEAD STATUS BY ID
    async def update_lead_status(self, lead_id: UUID, payload: LeadUpdateStatus):
        lead = await self.repo.get_by_id(lead_id=lead_id)
        if not lead:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Lead not found"
            )

        return await self.repo.update_status(lead=lead, payload=payload, load_user=True, load_contact=True)

    # DELETE LEAD STATUS BY ID
    async def delete_lead(self, lead_id: UUID):
        lead = await self.repo.get_by_id(lead_id=lead_id)
        if not lead:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Lead not found"
            )

        return await self.repo.delete(lead=lead)
