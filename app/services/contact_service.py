from math import ceil
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.app_exception import AppException, ErrorCode
from app.models.contact_model import Contact
from app.repositories.contact_repository import ContactRepository
from app.schemas.contact_schema import (
    ContactCreate, ContactUpdate,
    NoteCreate, TaskCreate
)


class ContactService:
    def __init__(self, db: AsyncSession):
        self.repo = ContactRepository(db)

    async def create_contact(self, user_id: UUID, data: ContactCreate):
        contact = await self.repo.create(Contact(user_id=user_id, **data.model_dump()))
        return contact

    async def find_all_contacts(self, user_id: UUID, query):
        contacts, total = await self.repo.get_all(user_id=user_id, query=query)
        total_pages = ceil(total / query.limit) if total else 1

        return {
            "total": total,
            "page": query.page,
            "limit": query.limit,
            "total_pages": total_pages,
            "data": contacts
        }

    async def find_one_contact(self, user_id: UUID, contact_id: int):
        contact = await self.repo.get_by_id(user_id=user_id, contact_id=contact_id)
        if not contact:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Contact not found"
            )
        return contact

    async def update_contact(self, user_id: int, contact_id: int, data: ContactUpdate):
        contact = await self.repo.get_by_id(user_id=user_id, contact_id=contact_id)
        if not contact:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Contact not found"
            )
        return await self.repo.update(contact, data)

    async def delete_contact(self, user_id: int, contact_id: int):
        contact = await self.repo.get_by_id(user_id=user_id, contact_id=contact_id)
        if not contact:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Contact not found"
            )
        return await self.repo.delete(contact)

    async def create_note(self, user_id: int, contact_id: int, data: NoteCreate):
        contact = await self.repo.get_by_id(user_id=user_id, contact_id=contact_id)
        if not contact:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Contact not found"
            )
        return await self.repo.create_note(contact_id, data)

    async def get_notes(self, user_id: int, contact_id: int):
        contact = await self.repo.get_by_id(user_id=user_id, contact_id=contact_id)
        if not contact:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Contact not found"
            )
        return await self.repo.get_notes(contact_id)

    async def create_task(self, user_id: int, contact_id: int, data: TaskCreate):
        contact = await self.repo.get_by_id(user_id=user_id, contact_id=contact_id)
        if not contact:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Contact not found"
            )
        return await self.repo.create_task(contact_id, data)

    async def get_tasks(self, user_id: int, contact_id: int):
        contact = await self.repo.get_by_id(user_id=user_id, contact_id=contact_id)
        if not contact:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Contact not found"
            )
        return await self.repo.get_tasks(contact_id)
