from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select, asc, desc
from app.models.contact_model import Contact, ContactNote, ContactTask
from app.schemas.contact_schema import ContactCreate, ContactUpdate, ContactRes, ContactResponse, NoteCreate, NoteResponse, TaskCreate, TaskResponse, PaginatedContacts


async def create_contact(db: AsyncSession, user_id: int, data: ContactCreate):
    new_contact = Contact(user_id=user_id, **data.dict())
    db.add(new_contact)
    await db.commit()
    await db.refresh(new_contact)
    return new_contact


async def find_all_contacts(
    db: AsyncSession,
    user_id: int,
    page: int = 1,
    limit: int = 10,
    search: str = None,
    sort_by: str = "name",
    sort_order: str = "asc"
):
    query = select(Contact).where(Contact.user_id == user_id)

    if search:
        query = query.where(
            Contact.name.ilike(f"%{search}%") |
            Contact.email.ilike(f"%{search}%") |
            Contact.company.ilike(f"%{search}%")
        )

    sort_column = getattr(Contact, sort_by, Contact.name)
    query = query.order_by(asc(sort_column) if sort_order == "asc" else desc(sort_column))

    total = await db.scalar(
        select(func.count(Contact.id)).where(Contact.user_id == user_id)
    )

    results = await db.execute(
        query.offset((page - 1) * limit).limit(limit)
    )

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": results.scalars().all()
    }


async def find_one_contact(db: AsyncSession, user_id: int, contact_id: int):
    result = await db.execute(
        select(Contact).where(
            Contact.id == contact_id,
            Contact.user_id == user_id
        )
    )
    return result.scalar_one_or_none()


async def update_contact(db: AsyncSession, user_id: int, contact_id: int, data: ContactUpdate):
    contact = await find_one_contact(db, user_id, contact_id)
    if not contact:
        return None

    for key, value in data.dict(exclude_unset=True).items():
        setattr(contact, key, value)

    await db.commit()
    await db.refresh(contact)
    return contact

async def delete_contact(db: AsyncSession, user_id: int, contact_id: int):
    contact = await find_one_contact(db, user_id, contact_id)
    if not contact:
        return False

    await db.delete(contact)
    await db.commit()
    return True


async def create_note(db: AsyncSession, user_id: int, contact_id: int, data: NoteCreate):
    contact = await find_one_contact(db, user_id, contact_id)
    if not contact:
        return None

    note = ContactNote(
        contact_id=contact_id,
        note=data.note
    )

    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


async def get_notes(db: AsyncSession, user_id: int, contact_id: int):
    contact = await find_one_contact(db, user_id, contact_id)
    if not contact:
        return None

    result = await db.execute(
        select(ContactNote).where(ContactNote.contact_id == contact_id)
    )
    return result.scalars().all()

async def create_task(db: AsyncSession, user_id: int, contact_id: int, data: TaskCreate):
    contact = await find_one_contact(db, user_id, contact_id)
    if not contact:
        return None

    task = ContactTask(
        contact_id=contact_id,
        task_name=data.task_name,
        date=data.date,
        priority=data.priority,
        assign_to_contact=data.assign_to_contact
    )

    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task

async def get_tasks(db: AsyncSession, user_id: int, contact_id: int):
    contact = await find_one_contact(db, user_id, contact_id)
    if not contact:
        return None

    result = await db.execute(
        select(ContactTask).where(ContactTask.contact_id == contact_id)
    )
    return result.scalars().all()
