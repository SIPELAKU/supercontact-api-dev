from sqlmodel import Session

from .seed_leads_test import seed_leads_test
from .seed_users_test import seed_users_test


def seed_all_test(db: Session):
    seed_users_test(db)
    seed_leads_test(db)
