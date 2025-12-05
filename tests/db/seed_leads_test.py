from datetime import date

from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Lead, LeadStatus, LeadSource, User


async def seed_leads_test(db: AsyncSession):
    result = await db.scalars(select(User))
    users = result.all()
    for i in range(5):
        lead = Lead(
            lead_name=f"Lead {i}",
            source=LeadSource.WEB_FORM,
            contact=f"testing {i}",
            status=LeadStatus.PROPOSAL,
            assigned_to=users[1].id,
            last_contacted=date(2025, 12, 12),
        )
        db.add(lead)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
