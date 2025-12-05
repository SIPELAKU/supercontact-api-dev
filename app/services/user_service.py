from sqlmodel.ext.asyncio.session import AsyncSession

from app.repositories import UserRepository


class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def find_all(self):
        users = await self.repo.get_all(load_leads=True)
        total = await self.repo.get_total()

        return {
            "total": total,
            "users": users,
        }
