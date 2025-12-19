from uuid import UUID
from datetime import datetime, time
from sqlalchemy.orm import selectinload
from sqlmodel import select, func, asc, desc
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.note_model import Note
from app.schemas import NoteCreate, NoteGetQuery


class NoteRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, note: Note):
        self.db.add(note)
        await self.db.commit()
        await self.db.refresh(note)
        return note

    # async def get_all(self, query):
    #     q = select(Note)

    #     total = await self.db.scalar(select(func.count(Note.id)))
    #     if query.limit == 0:
    #         result = await self.db.scalars(q)
    #         return result.all(), total

    #     if query.search:
    #         like = f"%{query.search}%"
    #         q = q.where(
    #             Note.title.ilike(like)
    #         )

    #     offset = (query.page - 1) * query.limit

    #     result = await self.db.scalars(
    #         q.offset(offset).limit(query.limit)
    #     )
    #     return result.all(), total

    async def get_all(self, query: NoteGetQuery):
        q = select(Note)

        # search title
        if query.search:
            like = f"%{query.search}%"
            q = q.where(Note.title.ilike(like))

        # filter created date
        if query.date_from:
            q = q.where(
                Note.created_at >= datetime.combine(query.date_from, time.min)
            )

        if query.date_to:
            q = q.where(
                Note.created_at <= datetime.combine(query.date_to, time.max)
            )

        # sorting
        if query.sort_by == "created_at":
            order_col = Note.created_at
        else:
            order_col = Note.title

        if query.sort_order == "asc":
            q = q.order_by(order_col.asc())
        else:
            q = q.order_by(order_col.desc())

        # total data (pakai query yg sama tapi tanpa limit)
        total = await self.db.scalar(
            select(func.count()).select_from(q.subquery())
        )

        # pagination
        if query.limit == 0:
            result = await self.db.scalars(q)
            return result.all(), total

        offset = (query.page - 1) * query.limit
        result = await self.db.scalars(
            q.offset(offset).limit(query.limit)
        )

        return result.all(), total

    async def update(self, note: Note, payload):
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(note, key, value)

        await self.db.commit()
        await self.db.refresh(note)
        return note
