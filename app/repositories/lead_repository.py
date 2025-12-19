from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import select, func, desc, asc
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import User, Lead, Contact, ContactNote
from app.schemas import LeadRequest, LeadUpdateStatus, LeadGetQuery, SortOrder


class LeadRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_assigned_to(self, assigned_to: UUID):
        return await self.db.get(User, assigned_to)

    async def create(self, payload: LeadRequest, load_user: bool = False, load_contact: bool = False):
        lead = Lead(**payload.model_dump())
        self.db.add(lead)
        await self.db.commit()
        await self.db.refresh(lead)
        return await self.get_by_id(lead_id=lead.id, load_user=load_user, load_contact=load_contact)

    async def get_by_id(self, lead_id: UUID, load_user: bool = False, load_contact: bool = False):
        # Subquery untuk last_contacted per contact
        last_note_subq = (
            select(
                ContactNote.contact_id,
                func.max(ContactNote.created_at).label("last_contacted")
            )
            .group_by(ContactNote.contact_id)
            .subquery()
        )

        # Base query: Lead join Contact join subquery
        query = (
            select(Lead)
            .join(Lead.contact)
            .outerjoin(
                last_note_subq, last_note_subq.c.contact_id == Contact.id
            )
        )
        # Load relationships if needed
        if load_user or load_contact:
            query = query.options(
                selectinload(Lead.user) if load_user else None,
                selectinload(Lead.contact).selectinload(Contact.notes) if load_contact else None
            )
        return await self.db.scalar(query)

    async def get_all(self, query_params: LeadGetQuery, load_user: bool = False, load_contact: bool = False):
        # Subquery untuk last_contacted per contact
        last_note_subq = (
            select(
                ContactNote.contact_id,
                func.max(ContactNote.created_at).label("last_contacted")
            )
            .group_by(ContactNote.contact_id)
            .subquery()
        )

        # Base query: Lead join Contact join subquery
        query = (
            select(Lead)
            .join(Lead.contact)
            .outerjoin(
                last_note_subq, last_note_subq.c.contact_id == Contact.id
            )
        )

        # Filtering
        if query_params.lead_status:
            query = query.where(Lead.lead_status.in_(query_params.lead_status))
        if query_params.lead_source:
            query = query.where(Lead.lead_source.in_(query_params.lead_source))
        if query_params.assigned_to:
            query = query.where(Lead.assigned_to.in_(query_params.assigned_to))

        if query_params.date_from:
            query = query.where(
                last_note_subq.c.last_contacted >= datetime.combine(query_params.date_from, datetime.min.time())
            )
        if query_params.date_to:
            query = query.where(
                last_note_subq.c.last_contacted <= datetime.combine(query_params.date_to, datetime.max.time())
            )

        if query_params.search:
            query = query.join(Lead.contact).where(Contact.name.ilike(f"%{query_params.search}%"))

        # Sorting
        if query_params.sort_order == SortOrder.DESC:
            query = query.order_by(desc(Lead.created_at))
        else:
            query = query.order_by(asc(Lead.created_at))

        # Load relationships if needed
        if load_user or load_contact:
            query = query.options(
                selectinload(Lead.user) if load_user else None,
                selectinload(Lead.contact).selectinload(Contact.notes) if load_contact else None
            )

        # Total count
        total_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(total_query)

        # Pagination
        offset = (query_params.page - 1) * query_params.limit
        query = query.offset(offset).limit(query_params.limit)

        result = await self.db.scalars(query)
        leads = result.all()

        return leads, total

    async def update(self, lead: Lead, payload: LeadRequest, load_user: bool = False, load_contact: bool = False):
        update_data = payload.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(lead, key, value)
        lead.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(lead)

        return await self.get_by_id(lead_id=lead.id, load_user=load_user, load_contact=load_contact)

    async def update_status(
            self,
            lead: Lead,
            payload: LeadUpdateStatus,
            load_user: bool = False,
            load_contact: bool = False
    ):
        lead.lead_status = payload.lead_status
        lead.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(lead)

        return await self.get_by_id(lead_id=lead.id, load_user=load_user, load_contact=load_contact)

    async def delete(self, lead: Lead):
        await self.db.delete(lead)
        await self.db.commit()

        return True
