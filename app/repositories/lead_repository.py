from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import User, Lead
from app.schemas import LeadRequest, LeadUpdateStatus
from app.schemas.lead_schema import LeadGetQuery


class LeadRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_assigned_to(self, assigned_to: UUID):
        return await self.db.get(User, assigned_to)

    async def create(self, lead: Lead):
        self.db.add(lead)
        await self.db.commit()
        await self.db.refresh(lead)
        return lead

    async def get_by_id(self, lead_id: UUID, load_user: bool = False, load_contact: bool = False):
        query = select(Lead).where(Lead.id == lead_id)
        if load_user:
            query = query.options(selectinload(Lead.user))
        if load_contact:
            query = query.options(selectinload(Lead.))
        return await self.db.scalar(query)

    async def get_all(self, query_params: LeadGetQuery, load_user: bool = False):
        query = select(Lead)

        # Load User Relationship
        if load_user:
            query = query.options(selectinload(Lead.user))

        # FILTERING
        if query_params.status:
            query = query.where(Lead.status.in_(query_params.status))
        if query_params.source:
            query = query.where(Lead.source.in_(query_params.source))
        if query_params.assigned_to:
            query = query.where(Lead.assigned_to.in_(query_params.assigned_to))

        # DATE RANGE
        if query_params.date_from:
            query = query.where(Lead.last_contacted >= datetime.combine(query_params.date_from, datetime.min.time()))
        if query_params.date_to:
            query = query.where(Lead.last_contacted <= datetime.combine(query_params.date_to, datetime.min.time()))

        # SEARCH BY LEAD NAME
        if query_params.search:
            query = query.where(Lead.lead_name.ilike(f"%{query_params.search}%"))

        # SORTING BY LAST_CONTACTED OR CREATED_AT
        sort_column = getattr(Lead, query_params.sort_by)
        if query_params.sort_order == "desc":
            sort_column = sort_column.desc()
        else:
            sort_column = sort_column.asc()
        query = query.order_by(sort_column)

        total_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(total_query)

        # PAGINATION
        offset = (query_params.page - 1) * query_params.limit
        result = await self.db.scalars(query.offset(offset).limit(query_params.limit))
        leads = result.all()

        return leads, total

    async def update(self, lead: Lead, payload: LeadRequest, load_user: bool = False):
        update_data = payload.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(lead, key, value)
        lead.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(lead)

        return await self.get_by_id(lead_id=lead.id, load_user=load_user)

    async def update_status(self, lead: Lead, payload: LeadUpdateStatus, load_user: bool = False):
        lead.status = payload.lead_status
        lead.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(lead)

        return await self.get_by_id(lead_id=lead.id, load_user=load_user)
