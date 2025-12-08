from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import auth_require
from app.db.session import get_async_session
from app.models import User
from app.schemas import ResponseModel, ContactListResponse, ContactResponse, ContactRequest
from app.services import ContactService

router = APIRouter(prefix="/contacts", tags=["Contacts"])


async def get_contact_service(db: AsyncSession = Depends(get_async_session)):
    return ContactService(db)


@router.get("/", response_model=ResponseModel[ContactListResponse])
async def get_all_contacts(
        page: int = 1,
        limit: int = 10,
        search: str = None,
        sort_by: str = "name",
        sort_order: str = "asc",
        service: ContactService = Depends(get_contact_service),
        current_user=Depends(auth_require)
):
    query = type("Query", (), {
        "page": page,
        "limit": limit,
        "search": search,
        "sort_by": sort_by,
        "sort_order": sort_order
    })
    data = await service.find_all_contacts(user_id=current_user.id, query=query)

    return ResponseModel(data=ContactListResponse(**data))


@router.post("/", response_model=ResponseModel[ContactResponse])
async def create_contact(
        data: ContactRequest,
        service: ContactService = Depends(get_contact_service),
        current_user=Depends(auth_require)
):
    contact = await service.create_contact(current_user.id, data)

    return ResponseModel(data=contact)


@router.get("/{contact_id}", response_model=ResponseModel[ContactResponse])
async def get_contact_by_id(
        contact_id: UUID,
        current_user: User = Depends(auth_require),
        service: ContactService = Depends(get_contact_service),
):
    contact = await service.find_one_contact(current_user.id, contact_id)

    return ResponseModel(data=contact)


@router.put("/{contact_id}", response_model=ResponseModel[ContactResponse])
async def update_contact_by_id(
        contact_id: UUID,
        data: ContactRequest,
        current_user: User = Depends(auth_require),
        service: ContactService = Depends(get_contact_service)
):
    updated = await service.update_contact(current_user.id, contact_id, data)

    return ResponseModel(data=updated)


@router.delete("/{contact_id}")
async def delete_contact_by_id(
        contact_id: UUID,
        current_user: User = Depends(auth_require),
        service: ContactService = Depends(get_contact_service)
):
    data = await service.delete_contact(current_user.id, contact_id)

    return ResponseModel(data=data)
#
#
# @router.post("/{contact_id}/notes", response_model=NoteResponse)
# async def create_note(
#         contact_id: int,
#         data: NoteCreate,
#         db: AsyncSession = Depends(get_async_session),
#         current_user: User = Depends(get_current_user)

# ):
#     service = ContactService(db)
#     return await service.create_note(current_user.id, contact_id, data)
#
#
# # GET NOTES
# @router.get("/{contact_id}/notes", response_model=list[NoteResponse])
# async def get_all_notes(
#         contact_id: int,
#         db: AsyncSession = Depends(get_async_session),
#         current_user: User = Depends(get_current_user)
# ):
#     service = ContactService(db)
#     return await service.get_notes(current_user.id, contact_id)
#
#
# # CREATE TASK
# @router.post("/{contact_id}/tasks", response_model=TaskResponse)
# async def create_task(
#         contact_id: int,
#         data: TaskCreate,
#         db: AsyncSession = Depends(get_async_session),
#         current_user: User = Depends(get_current_user)
# ):
#     service = ContactService(db)
#     return await service.create_task(current_user.id, contact_id, data)
#
#
# # GET TASKS
# @router.get("/{contact_id}/tasks", response_model=list[TaskResponse])
# async def get_all_tasks(
#     contact_id: int,
#     db: AsyncSession = Depends(get_async_session),
#     current_user: User = Depends(get_current_user)
# ):
#     service = ContactService(db)
#     return await service.get_tasks(current_user.id, contact_id)
