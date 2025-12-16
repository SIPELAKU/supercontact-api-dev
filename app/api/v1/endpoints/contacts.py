from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import auth_require
from app.db.session import get_async_session
from app.models import User
from app.schemas import (
    ContactCreate,
    ContactUpdate,
    PaginatedContacts,
    NoteCreate,
    NoteResponse,
    TaskCreate,
    TaskResponse,
    ResponseModel,
    ContactResponse,
    ContactDeleteResponse,
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
    page: int = 1,
    limit: int = 10,
    search: str = None,
    sort_by: str = "name",
    sort_order: str = "asc",
    service: ContactService = Depends(get_contact_service),
):
    query = type(
        "Query",
        (),
        {
            "page": page,
            "limit": limit,
            "search": search,
            "sort_by": sort_by,
            "sort_order": sort_order,
        },
    )
    result = await service.find_all_contacts(query=query)
    return ResponseModel(
        data=PaginatedContacts(
            total=result["total"],
            page=result["page"],
            limit=result["limit"],
            total_pages=result["total_pages"],
            contacts=result["contacts"],
        )
    )


@router.post(
    "/",
    response_model=ResponseModel[ContactResponse],
    dependencies=[Depends(auth_require)],
)
async def create_contact(
    data: ContactCreate,
    service: ContactService = Depends(get_contact_service),
    current_user=Depends(auth_require),
):
    contact = await service.create_contact(user_id=current_user.id, data=data)

    return ResponseModel(data=contact)


@router.get(
    "/{contact_id}",
    response_model=ResponseModel[ContactResponse],
    dependencies=[Depends(auth_require)],
)
async def get_contact_by_id(
    contact_id: UUID,
    service: ContactService = Depends(get_contact_service),
    current_user: User = Depends(auth_require),
):
    contact = await service.find_one_contact(
        user_id=current_user.id, contact_id=contact_id
    )

    return ResponseModel(data=contact)


@router.put("/{contact_id}", response_model=ResponseModel[ContactResponse])
async def update_contact_by_id(
    contact_id: UUID,
    data: ContactUpdate,
    service: ContactService = Depends(get_contact_service),
    current_user: User = Depends(auth_require),
):
    updated = await service.update_contact(
        user_id=current_user.id, contact_id=contact_id, data=data
    )

    return ResponseModel(data=updated)


@router.delete("/{contact_id}", response_model=ResponseModel[ContactDeleteResponse])
async def delete_contact_by_id(
    contact_id: UUID,
    service: ContactService = Depends(get_contact_service),
    current_user: User = Depends(auth_require),
):
    contact = await service.delete_contact(
        user_id=current_user.id, contact_id=contact_id
    )

    return ResponseModel(data={"id": contact_id, "deleted": contact})


@router.post(
    "/{contact_id}/notes",
    response_model=ResponseModel[NoteResponse],
    dependencies=[Depends(auth_require)],
)
async def create_note(
    contact_id: UUID,
    data: NoteCreate,
    service: ContactService = Depends(get_contact_service),
    current_user: User = Depends(auth_require),
):
    note = await service.create_note(
        user_id=current_user.id, contact_id=contact_id, data=data
    )
    return ResponseModel(data=note)


# GET NOTES
@router.get("/{contact_id}/notes", response_model=ResponseModel[list[NoteResponse]])
async def get_all_notes(
    contact_id: UUID,
    service: ContactService = Depends(get_contact_service),
    current_user: User = Depends(auth_require),
):
    note = await service.get_notes(user_id=current_user.id, contact_id=contact_id)
    return ResponseModel(data=note)


# CREATE TASK
@router.post(
    "/{contact_id}/tasks",
    response_model=ResponseModel[TaskResponse],
    dependencies=[Depends(auth_require)],
)  #
async def create_task(
    contact_id: UUID,
    data: TaskCreate,
    service: ContactService = Depends(get_contact_service),
    current_user: User = Depends(auth_require),
):
    task = await service.create_task(
        user_id=current_user.id, contact_id=contact_id, data=data
    )
    return ResponseModel(data=task)


# GET TASKS
@router.get("/{contact_id}/tasks", response_model=list[TaskResponse])
async def get_all_tasks(
    contact_id: UUID,
    service: ContactService = Depends(get_contact_service),
    current_user: User = Depends(auth_require),
):
    return await service.get_tasks(user_id=current_user.id, contact_id=contact_id)
