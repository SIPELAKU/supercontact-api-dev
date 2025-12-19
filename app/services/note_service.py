from math import ceil
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.app_exception import AppException, ErrorCode
from app.models.note_model import Note
from app.repositories.note_repository import NoteRepository
from app.schemas import NoteGetQuery
from app.schemas.note_schema import NoteCreate, NoteUpdate
from sqlalchemy import select



class NoteService:
    def __init__(self, db: AsyncSession):
        self.repo = NoteRepository(db)

    async def create_note(self, user_id: UUID, data: NoteCreate):
        note = await self.repo.create(
            Note(
                user_id=user_id, **data.model_dump()
            )
        )
        return note

    async def find_all_notes(self, query: NoteGetQuery):
        notes, total = await self.repo.get_all(query=query)
        total_pages = ceil(total / query.limit) if total else 1

        return {
            "total": total,
            "page": query.page,
            "limit": query.limit,
            "total_pages": total_pages,
            "notes": notes
        }

    async def update_note(self, user_id: UUID, note_id: UUID, data: NoteUpdate):
        # note = await self.repo.update(note_id=note_id)
        result = await self.repo.db.execute(
            select(Note).where(
                Note.id == note_id,
                Note.user_id == user_id
            )
        )
        note = result.scalar_one_or_none()
        if not note:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Contact not found"
            )
        return await self.repo.update(note, data)