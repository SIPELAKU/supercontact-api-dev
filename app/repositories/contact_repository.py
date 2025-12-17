from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import select, func, asc, desc
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.contact_model import Contact, ContactNote, ContactTask
from app.schemas import ContactGetQuery, ContactSortOrder, ContactSortBy


class ContactRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, contact: Contact):
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def get_by_id(self, contact_id: UUID):
        query = (
            select(Contact)
            .where(Contact.id == contact_id)
        )
        return await self.db.scalar(query)

    async def get_all(self, query: ContactGetQuery):
        q = select(Contact)

        total = await self.db.scalar(select(func.count(Contact.id)))
        if query.limit == 0:
            result = await self.db.scalars(q)
            return result.all(), total

        if query.search:
            like = f"%{query.search}%"
            q = q.where(
                Contact.name.ilike(like) |
                Contact.email.ilike(like) |
                Contact.company.ilike(like)
            )
        if query.sort_by == ContactSortBy.NAME:
            sort_column = getattr(Contact, query.sort_by, Contact.name)
        elif query.sort_by == ContactSortBy.CREATED_AT:
            sort_column = getattr(Contact, query.sort_by, Contact.created_at)
            
        q = q.order_by(
            asc(sort_column) if query.sort_order == ContactSortOrder.ASC else desc(sort_column)
        )

        offset = (query.page - 1) * query.limit

        result = await self.db.scalars(
            q.offset(offset).limit(query.limit)
        )
        return result.all(), total

    async def update(self, contact: Contact, payload):
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(contact, key, value)

        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def delete(self, contact: Contact):
        await self.db.delete(contact)
        await self.db.commit()
        return True

    async def create_note(self, user_id: UUID, contact_id: UUID, data):
        note = ContactNote(user_id=user_id, contact_id=contact_id, note=data.note)
        self.db.add(note)
        await self.db.commit()
        await self.db.refresh(note)
        query = (
            select(ContactNote).options(
                selectinload(ContactNote.user),
            )
            .where(ContactNote.id == note.id)
        )
        return await self.db.scalar(query)

    async def get_notes(self, contact_id: UUID):
        result = await self.db.scalars(
            select(ContactNote).options(
                selectinload(ContactNote.user),
            )
            .where(ContactNote.contact_id == contact_id)
        )
        return result.all()

    async def create_task(self, contact_id: UUID, data):
        task = ContactTask(
            contact_id=contact_id,
            task_name=data.task_name,
            task_date=data.task_date,
            priority=data.priority,
            assign_to=data.assign_to
        )
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)

        query = (
            select(ContactTask).options(
                selectinload(ContactTask.user),
            )
            .where(ContactTask.id == task.id)
        )
        return await self.db.scalar(query)

    async def get_tasks(self, contact_id: UUID):
        result = await self.db.scalars(
            select(ContactTask).options(
                selectinload(ContactTask.user)
            )
            .where(ContactTask.contact_id == contact_id)
        )
        return result.all()
