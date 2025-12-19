from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import auth_require
from app.db.session import get_async_session
from app.models import User
from app.schemas import (
    ContactCreate, ContactUpdate,
    PaginatedContacts,
    ContactNoteCreate,
    ContactNoteResponse,
    ContactTaskCreate,
    ContactTaskResponse,
    ResponseModel,
    ContactResponse,
    ContactDeleteResponse,
    ContactSortBy,
    ContactSortOrder,
    ContactGetQuery
)
from app.services.contact_service import ContactService

router = APIRouter(prefix="/contacts", tags=["Contacts"])


async def get_contact_service(db: AsyncSession = Depends(get_async_session)):
    return ContactService(db=db)


@router.get(
    "/",
    response_model=ResponseModel[PaginatedContacts],
    # dependencies=[Depends(auth_require)]
)
async def get_all_contacts(
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100, ),
        search: str = Query(None),
        sort_by: ContactSortBy = Query(ContactSortBy.CREATED_AT),
        sort_order: ContactSortOrder = Query(ContactSortOrder.DESC),
        service: ContactService = Depends(get_contact_service),
):
    query = ContactGetQuery(
        page=page,
        limit=limit,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    result = await service.find_all_contacts(query=query)
    return ResponseModel(data=PaginatedContacts(
        total=result["total"],
        page=result["page"],
        limit=result["limit"],
        total_pages=result["total_pages"],
        contacts=result["contacts"]
    ))


@router.post(
    "/",
    response_model=ResponseModel[ContactResponse],
    # dependencies=[Depends(auth_require)]
)
async def create_contact(
        data: ContactCreate,
        service: ContactService = Depends(get_contact_service),
):
    contact = await service.create_contact(data=data)

    return ResponseModel(data=contact)


@router.get(
    "/{contact_id}",
    response_model=ResponseModel[ContactResponse],
    # dependencies=[Depends(auth_require)]
)
async def get_contact_by_id(contact_id: UUID, service: ContactService = Depends(get_contact_service)):
    contact = await service.find_one_contact(contact_id=contact_id)

    return ResponseModel(data=contact)


@router.put(
    "/{contact_id}",
    response_model=ResponseModel[ContactResponse],
    # dependencies=[Depends(auth_require)]
)
async def update_contact_by_id(
        contact_id: UUID,
        data: ContactUpdate,
        service: ContactService = Depends(get_contact_service)
):
    updated = await service.update_contact(contact_id=contact_id, data=data)

    return ResponseModel(data=updated)


@router.delete(
    "/{contact_id}",
    response_model=ResponseModel[ContactDeleteResponse],
    # dependencies=[Depends(auth_require)]
)
async def delete_contact_by_id(
        contact_id: UUID,
        service: ContactService = Depends(get_contact_service)
):
    contact = await service.delete_contact(contact_id=contact_id)

    return ResponseModel(data={"id": contact_id, "deleted": contact})


@router.post(
    "/{contact_id}/notes",
    response_model=ResponseModel[ContactNoteResponse],
)
async def create_note(
        contact_id: UUID,
        data: ContactNoteCreate,
        service: ContactService = Depends(get_contact_service),
        current_user: User = Depends(auth_require)
):
    note = await service.create_note(user_id=current_user.id, contact_id=contact_id, data=data)
    return ResponseModel(data=note)


# GET NOTES
@router.get(
    "/{contact_id}/notes",
    response_model=ResponseModel[list[ContactNoteResponse]]
)
async def get_all_notes(
        contact_id: UUID,
        service: ContactService = Depends(get_contact_service),
):
    note = await service.get_notes(contact_id=contact_id)
    return ResponseModel(data=note)


# CREATE TASK
@router.post(
    "/{contact_id}/tasks",
    response_model=ResponseModel[ContactTaskResponse],
    # dependencies=[Depends(auth_require)]
)
async def create_task(
        contact_id: UUID,
        data: ContactTaskCreate,
        service: ContactService = Depends(get_contact_service),
):
    task = await service.create_task(contact_id=contact_id, data=data)
    return ResponseModel(data=task)


# GET TASKS
@router.get(
    "/{contact_id}/tasks",
    response_model=ResponseModel[list[ContactTaskResponse]],
    # dependencies=[Depends(auth_require)]
)
async def get_all_tasks(
        contact_id: UUID,
        service: ContactService = Depends(get_contact_service),
):
    task = await service.get_tasks(contact_id=contact_id)
    return ResponseModel(data=task)
