import argparse
import asyncio
from datetime import date
from typing import Optional
from uuid import UUID

from faker import Faker
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.db.session import get_async_session
from app.models import LeadIndustry, LeadCompanySize, LeadOfficeLocation, Contact
from app.models.lead_model import LeadSource, LeadStatus, Lead
from app.models.user_model import User

faker = Faker()


async def seed_leads(total: int = 10, user_id: Optional[UUID] = None):
    db_gen = get_async_session()
    db = await anext(db_gen)
    query = await db.scalars(select(Contact))
    contacts = query.all()
    query = await db.scalars(select(User))
    users = query.all()
    for i in range(total):
        lead = Lead(
            lead_name=contacts[0].id,
            industry=LeadIndustry.FINANCE,
            company_size=LeadCompanySize.SMALL,
            office_location=LeadOfficeLocation.JAKARTA,
            lead_status=LeadStatus.PROPOSAL,
            lead_source=LeadSource.WEB_FORM,
            assigned_to=users[1].id if not user_id else user_id,
            last_contacted=date(2025, 12, 12),
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
    args = parser.parse_args()

    print(f"Running database seed for {args.total} leads...")
    asyncio.run(seed_leads(args.total, args.user_id))
    print("Seed completed!")
