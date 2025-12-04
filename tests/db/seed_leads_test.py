from datetime import date

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.models import Lead, LeadStatus, LeadSource, User


def seed_leads_test(db: Session):
    user_db = db.exec(select(User)).all()
    for i in range(5):
        lead = Lead(
            lead_name=f"Lead {i}",
            source=LeadSource.WEB_FORM,
            contact=f"testing {i}",
            status=LeadStatus.PROPOSAL,
            assigned_to=user_db[1].id,
            last_contacted=date(2025, 12, 12),
        )
        db.add(lead)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
