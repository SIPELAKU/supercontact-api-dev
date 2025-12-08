from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
<<<<<<< Updated upstream

from app.core import auth_require
from app.db.session import get_async_session
from app.schemas import (
    ContactCreate,
    ContactResponse,
    PaginatedContacts,
    ContactRes
)
from app.services.contact_service import ContactService

router = APIRouter(prefix="/contacts", tags=["Contacts"])


async def get_contact_service(db: AsyncSession = Depends(get_async_session)):
    return ContactService(db)


=======

from app.db.session import get_async_session
from app.schemas.contact_schema import PaginatedContacts, ContactRes
from app.services.contact_service import ContactService

router = APIRouter(prefix="/contacts", tags=["Contacts"])


>>>>>>> Stashed changes
@router.get("/", response_model=PaginatedContacts)
async def get_all_contacts(
        page: int = 1,
        limit: int = 10,
        search: str = None,
        sort_by: str = "name",
        sort_order: str = "asc",
<<<<<<< Updated upstream
        service: ContactService = Depends(get_contact_service),
        current_user=Depends(auth_require)
=======
        db: AsyncSession = Depends(get_async_session),
        # current_user = Depends(get_current_user)
>>>>>>> Stashed changes
):
    query = type("Query", (), {
        "page": page,
        "limit": limit,
        "search": search,
        "sort_by": sort_by,
        "sort_order": sort_order
    })
    result = await service.find_all_contacts(user_id=current_user.id, query=query)
    contacts = [ContactRes.model_validate(c) for c in result["data"]]

    return PaginatedContacts(
        status="success",
        message="Contact List",
        total=result["total"],
        page=result["page"],
        limit=result["limit"],
        total_pages=result["total_pages"],
        data=contacts
    )

<<<<<<< Updated upstream

@router.post("/", response_model=ContactResponse)
async def create_contact(
        data: ContactCreate,
        service: ContactService = Depends(get_contact_service),
        current_user=Depends(auth_require)
):
    contact = await service.create_contact(current_user.id, data)
    service = ContactService(db)
    contact = await service.create_contact(user.id, data)

    return ContactResponse(
        status="success",
        message="Contact created successfully.",
        data=contact
    )

# @router.get("/{contact_id}", response_model=ContactResponse)
# async def get_contact_by_id(contact_id: int, db: AsyncSession = Depends(get_async_session),
#                             current_user: User = Depends(get_current_user)):
=======
# @router.post("/", response_model=ContactResponse)
# async def create_contact(
#     data: ContactCreate,
#     db: AsyncSession = Depends(get_async_session),
#     # current_user: User = Depends(get_current_user)
#     dependencies=[Depends(auth_require)]
# ):
#
#     # service = ContactService(db)
#     # contact = await service.create_contact(current_user.id, data)
#     service = ContactService(db)
#     contact = await service.create_contact(user.id, data)
#
#     return ContactResponse(
#         status="success",
#         message="Contact created successfully.",
#         data=contact
#     )
#
# @router.get("/{contact_id}", response_model=ContactResponse)
# async def get_contact_by_id(contact_id: int, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
>>>>>>> Stashed changes
#     service = ContactService(db)
#     contact = await service.find_one_contact(current_user.id, contact_id)
#
#     return ContactResponse(
#         status="success",
#         message="Contact detail.",
#         data=contact
#     )
#
<<<<<<< Updated upstream
#
# @router.put("/{contact_id}", response_model=ContactResponse)
# async def update_contact_by_id(contact_id: int, data: ContactUpdate, db: AsyncSession = Depends(get_async_session),
#                                current_user: User = Depends(get_current_user)):
=======
# @router.put("/{contact_id}", response_model=ContactResponse)
# async def update_contact_by_id(contact_id: int, data: ContactUpdate, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
>>>>>>> Stashed changes
#     service = ContactService(db)
#     updated = await service.update_contact(current_user.id, contact_id, data)
#
#     return ContactResponse(
#         status="success",
#         message="Contact updated successfully.",
#         data=updated
#     )
#
<<<<<<< Updated upstream
#
# @router.delete("/{contact_id}")
# async def delete_contact_by_id(contact_id: int, db: AsyncSession = Depends(get_async_session),
#                                current_user: User = Depends(get_current_user)):
=======
# @router.delete("/{contact_id}")
# async def delete_contact_by_id(contact_id: int, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
>>>>>>> Stashed changes
#     service = ContactService(db)
#     await service.delete_contact(current_user.id, contact_id)
#
#     return DeleteResponse(
#         status="success",
#         message="Contact deleted successfully"
#     )
#
<<<<<<< Updated upstream
#
# @router.post("/{contact_id}/notes", response_model=NoteResponse)
# async def create_note(
#         contact_id: int,
#         data: NoteCreate,
#         db: AsyncSession = Depends(get_async_session),
#         current_user: User = Depends(get_current_user)
=======
# @router.post("/{contact_id}/notes", response_model=NoteResponse)
# async def create_note(
#     contact_id: int,
#     data: NoteCreate,
#     db: AsyncSession = Depends(get_async_session),
#     current_user: User = Depends(get_current_user)
>>>>>>> Stashed changes
# ):
#     service = ContactService(db)
#     return await service.create_note(current_user.id, contact_id, data)
#
#
# # GET NOTES
# @router.get("/{contact_id}/notes", response_model=list[NoteResponse])
# async def get_all_notes(
<<<<<<< Updated upstream
#         contact_id: int,
#         db: AsyncSession = Depends(get_async_session),
#         current_user: User = Depends(get_current_user)
=======
#     contact_id: int,
#     db: AsyncSession = Depends(get_async_session),
#     current_user: User = Depends(get_current_user)
>>>>>>> Stashed changes
# ):
#     service = ContactService(db)
#     return await service.get_notes(current_user.id, contact_id)
#
#
# # CREATE TASK
# @router.post("/{contact_id}/tasks", response_model=TaskResponse)
# async def create_task(
<<<<<<< Updated upstream
#         contact_id: int,
#         data: TaskCreate,
#         db: AsyncSession = Depends(get_async_session),
#         current_user: User = Depends(get_current_user)
=======
#     contact_id: int,
#     data: TaskCreate,
#     db: AsyncSession = Depends(get_async_session),
#     current_user: User = Depends(get_current_user)
>>>>>>> Stashed changes
# ):
#     service = ContactService(db)
#     return await service.create_task(current_user.id, contact_id, data)
#
#
# # GET TASKS
# @router.get("/{contact_id}/tasks", response_model=list[TaskResponse])
# async def get_all_tasks(
<<<<<<< Updated upstream
#         contact_id: int,
#         db: AsyncSession = Depends(get_async_session),
#         current_user: User = Depends(get_current_user)
=======
#     contact_id: int,
#     db: AsyncSession = Depends(get_async_session),
#     current_user: User = Depends(get_current_user)
>>>>>>> Stashed changes
# ):
#     service = ContactService(db)
#     return await service.get_tasks(current_user.id, contact_id)
