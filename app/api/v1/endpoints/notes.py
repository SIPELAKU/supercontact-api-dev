from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import auth_require
from app.db.session import get_async_session
from app.models import User

from app.schemas import NoteCreate, NoteUpdate, PaginatedNote, NoteResponse, ResponseModel, NoteGetQuery
from app.services.note_service import NoteService


router = APIRouter(prefix="/notes", tags=["Notes"])


async def get_note_service(db: AsyncSession = Depends(get_async_session)):
    return NoteService(db=db)

@router.get(
    "/",
    response_model=ResponseModel[PaginatedNote],
    dependencies=[Depends(auth_require)]
)
async def get_all_notes(
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100, ),
        search: str = Query(None),
        service: NoteService = Depends(get_note_service),
):
    query = NoteGetQuery(
        page=page,
        limit=limit,
        search=search,
    )
    result = await service.find_all_notes(query=query)
    return ResponseModel(data=PaginatedNote(
        total=result["total"],
        page=result["page"],
        limit=result["limit"],
        total_pages=result["total_pages"],
        notes=result["notes"]
    ))

@router.post("/", response_model=ResponseModel[NoteResponse], dependencies=[Depends(auth_require)])
async def create_notes(
        data: NoteCreate,
        service: NoteService = Depends(get_note_service),
        current_user=Depends(auth_require),
):
    note = await service.create_note(user_id=current_user.id, data=data)

    return ResponseModel(data=note)


@router.put(
    "/{contact_id}",
    response_model=ResponseModel[NoteResponse],
    dependencies=[Depends(auth_require)]
)
async def update_note_by_id(
        note_id: UUID,
        data: NoteUpdate,
        service: NoteService = Depends(get_note_service),
        current_user=Depends(auth_require),
):
    updated = await service.update_note(
        user_id=current_user.id,
        note_id=note_id,
        data=data
    )

    return ResponseModel(data=updated)
