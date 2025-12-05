from sqlmodel.ext.asyncio.session import AsyncSession

from .seed_leads_test import seed_leads_test
from .seed_users_test import seed_users_test


async def seed_all_test(db: AsyncSession):
    await seed_users_test(db)
    await seed_leads_test(db)
