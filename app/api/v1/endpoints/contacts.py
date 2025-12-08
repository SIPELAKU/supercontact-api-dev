from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import auth_require
from app.db.session import get_async_session
from app.models import User
from app.schemas import (
    ContactCreate, ContactUpdate,
    PaginatedContacts,
    NoteCreate, NoteResponse,
    TaskCreate, TaskResponse,
    DeleteResponse, ResponseModel, ContactResponse
)
from app.services.contact_service import ContactService

router = APIRouter(prefix="/contacts", tags=["Contacts"])


@router.get("/", response_model=PaginatedContacts, dependencies=[Depends(auth_require)])
async def get_all_contacts(
        page: int = 1,
        limit: int = 10,
        search: str = None,
        sort_by: str = "name",
        sort_order: str = "asc",
        db: AsyncSession = Depends(get_async_session),
        current_user=Depends(auth_require)
):
    service = ContactService(db)

    query = type("Query", (), {
        "page": page,
        "limit": limit,
        "search": search,
        "sort_by": sort_by,
        "sort_order": sort_order
    })
    result = await service.find_all_contacts(user_id=current_user.id, query=query)
    contacts = [ContactResponse.model_validate(c) for c in result["data"]]

    return PaginatedContacts(
        status="success",
        message="Contact List",
        total=result["total"],
        page=result["page"],
        limit=result["limit"],
        total_pages=result["total_pages"],
        data=contacts
    )


@router.post("/", response_model=ResponseModel[ContactResponse],
             dependencies=[Depends(auth_require)])
async def create_contact(
        data: ContactCreate,
        db: AsyncSession = Depends(get_async_session),
        current_user=Depends(auth_require)
):
    service = ContactService(db)
    contact = await service.create_contact(user_id=current_user.id, data=data)

    return ContactResponse(
        status="success",
        message="Contact created successfully.",
        data=contact
    )


@router.get("/{contact_id}", response_model=ContactResponse, dependencies=[Depends(auth_require)])
async def get_contact_by_id(contact_id: UUID, db: AsyncSession = Depends(get_async_session),
                            current_user: User = Depends(auth_require)):
    service = ContactService(db)
    contact = await service.find_one_contact(user_id=current_user.id, contact_id=contact_id)

    return ContactResponse(
        status="success",
        message="Contact detail.",
        data=contact
    )


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact_by_id(contact_id: UUID, data: ContactUpdate, db: AsyncSession = Depends(get_async_session),
                               current_user: User = Depends(auth_require)):
    service = ContactService(db)
    updated = await service.update_contact(user_id=current_user.id, contact_id=contact_id, data=data)

    return ContactResponse(
        status="success",
        message="Contact updated successfully.",
        data=updated
    )


@router.delete("/{contact_id}")
async def delete_contact_by_id(contact_id: UUID, db: AsyncSession = Depends(get_async_session),
                               current_user: User = Depends(auth_require)):
    service = ContactService(db)
    await service.delete_contact(user_id=current_user.id, contact_id=contact_id)

    return DeleteResponse(
        status="success",
        message="Contact deleted successfully"
    )


@router.post("/{contact_id}/notes", response_model=NoteResponse, dependencies=[Depends(auth_require)])
async def create_note(
        contact_id: UUID,
        data: NoteCreate,
        db: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(auth_require)
):
    service = ContactService(db)
    return await service.create_note(user_id=current_user.id, contact_id=contact_id, data=data)


# GET NOTES
@router.get("/{contact_id}/notes", response_model=list[NoteResponse])
async def get_all_notes(
        contact_id: UUID,
        db: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(auth_require)
):
    service = ContactService(db)
    return await service.get_notes(user_id=current_user.id, contact_id=contact_id)


# CREATE TASK
@router.post("/{contact_id}/tasks", response_model=TaskResponse, dependencies=[Depends(auth_require)])
async def create_task(
        contact_id: UUID,
        data: TaskCreate,
        db: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(auth_require)
):
    service = ContactService(db)
    return await service.create_task(user_id=current_user.id, contact_id=contact_id, data=data)


# GET TASKS
@router.get("/{contact_id}/tasks", response_model=list[TaskResponse])
async def get_all_tasks(
        contact_id: UUID,
        db: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(auth_require)
):
    service = ContactService(db)
    return await service.get_tasks(user_id=current_user.id, contact_id=contact_id)
