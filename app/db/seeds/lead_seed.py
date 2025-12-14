import argparse
import asyncio
import random
from enum import StrEnum
from typing import Optional
from uuid import UUID

from faker import Faker
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.db.session import get_async_session
from app.models import (
    LeadIndustry,
    LeadCompanySize,
    LeadSource,
    LeadStatus,
    Lead,
    User,
    Contact, LeadTag,
)

faker = Faker()


class LeadOfficeLocation(StrEnum):
    JAKARTA = "DKI Jakarta"
    BANDUNG = "Bandung"
    YOGYAKARTA = "Yogyakarta"
    MALANG = "Malang"
    SURABAYA = "Surabaya"
    TEGAL = "Tegal"


async def seed_leads(total: int = 10, user_id: Optional[UUID] = None, contact_id: Optional[UUID] = None):
    db_gen = get_async_session()
    db = await anext(db_gen)
    query = await db.scalars(select(Contact))
    contacts = query.all()
    query = await db.scalars(select(User))
    users = query.all()
    for i in range(total):
        lead = Lead(
            contact_id=contacts[i % len(contacts)].id if not contact_id else contact_id,
            industry=random.choice(list(LeadIndustry)),
            company_size=random.choice(list(LeadCompanySize)),
            office_location=random.choice(list(LeadOfficeLocation)),
            lead_status=random.choice(list(LeadStatus)),
            lead_source=random.choice(list(LeadSource)),
            assigned_to=users[i % len(users)].id if not user_id else user_id,
            tag=random.choice(list(LeadTag)),
            notes=faker.sentence(),
        )
        db.add(lead)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
    finally:
        await db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed leads into the database.")
    parser.add_argument(
        "--total", type=int, default=10, help="Total number of leads to create"
    )
    parser.add_argument(
        "--user_id", type=UUID, help="Assign all leads to this user ID"
    )
    parser.add_argument(
        "--contact_id", type=UUID, help="Assign all leads to this contact ID"
    )
    args = parser.parse_args()

    print(f"Running database seed for {args.total} leads...")
    asyncio.run(seed_leads(total=args.total, user_id=args.user_id, contact_id=args.contact_id))
    print("Seed completed!")
