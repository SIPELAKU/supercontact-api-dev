from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from app.db.base import get_db
from app.schemas.contact_schema import *
from app.services.contact_service import *
from app.utils.jwt_util import get_current_user
from app.models.user_model import User
from app.db.session import get_async_session


router = APIRouter(prefix="/contacts", tags=["Contacts"])

@router.get("/", response_model=PaginatedContacts)
async def get_all_contacts(
    page: int = 1,
    limit: int = 10,
    search: str = None,
    sort_by: str = "name",
    sort_order: str = "asc",
    db: AsyncSession = Depends(get_async_session),
    current_user = Depends(get_current_user)
):
    result = find_all_contacts(db, current_user.id, page, limit, search, sort_by, sort_order)
    contacts = [ContactRes.model_validate(c) for c in result["data"]]
    return PaginatedContacts(
        status="success",
        message="Contact List",
        total=result["total"],
        page=result["page"],
        limit=result["limit"],
        data=contacts
    )

@router.post("/", response_model=ContactResponse)
async def create_contact(
    data: ContactCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user = Depends(get_current_user)
):

    contact = create_contact(db, current_user.id, data)

    return ContactResponse(
        status="success",
        message="Contact created successfully.",
        data=contact
    )

@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact_by_id(contact_id: int, db: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    contact = find_one_contact(db, current_user.id, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return ContactResponse(
        status="success",
        message="Contact detail.",
        data=contact
    )

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact_by_id(contact_id: int, data: ContactUpdate, db: AsyncSession = Depends(get_async_session), current_user = Depends(get_current_user)):
    updated = update_contact(db, current_user.id, contact_id, data)
    if not updated:
        raise HTTPException(404)
    return ContactResponse(
        status="success",
        message="Contact updated successfully.",
        data=updated
    )

@router.delete("/{contact_id}")
async def delete_contact_by_id(contact_id: int, db: AsyncSession = Depends(get_async_session), current_user = Depends(get_current_user)):
    result = delete_contact(db, current_user.id, contact_id)
    if not result:
        raise HTTPException(404)
    return DeleteResponse(
        status="success",
        message="Contact deleted successfully"
    )


@router.post("/{contact_id}/notes", response_model=NoteResponse)
async def create_note(contact_id: int, data: NoteCreate, db: AsyncSession = Depends(get_async_session), current_user = Depends(get_current_user)):
    return create_note(db, current_user.id, contact_id, data)

@router.get("/{contact_id}/notes", response_model=List[NoteResponse])
async def get_all_notes(contact_id: int, db: AsyncSession = Depends(get_async_session), current_user = Depends(get_current_user)):
    return get_notes(db, current_user.id, contact_id)


@router.post("/{contact_id}/tasks", response_model=TaskResponse)
async def create_task(contact_id: int, data: TaskCreate, db: AsyncSession = Depends(get_async_session), current_user = Depends(get_current_user)):
    return create_task(db, current_user.id, contact_id, data)

@router.get("/{contact_id}/tasks", response_model=List[TaskResponse])
async def get_all_tasks(contact_id: int, db: AsyncSession = Depends(get_async_session), current_user = Depends(get_current_user)):
    return get_tasks(db, current_user.id, contact_id)
