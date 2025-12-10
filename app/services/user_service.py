from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.schemas.user_schema import UserCreate, UserUpdate
from app.models.user_model import User, UserStatus
from app.repository.user_repository import UserRepository
from app.utils.hashing import Hasher


class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def create(self, data: UserCreate) -> User:
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        new_user = User(
            fullname=data.fullname,
            email=data.email,
            password=Hasher.hash(data.password),
            employee_id=data.employee_id,
            department_id=data.department_id,
            role_id=data.role_id,
            status=data.status or UserStatus.PENDING,
        )

        try:
            return await self.repo.create(new_user)
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate data detected",
            )

    async def get(self, user_id: UUID) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def list(self, search: str | None, limit: int = 10, offset: int = 0):
        return await self.repo.list(search, limit, offset)

    async def update(self, user_id: UUID, data: UserUpdate) -> User:
        user = await self.get(user_id)

        updates = data.dict(exclude_unset=True)
        if "password" in updates:
            updates["password"] = Hasher.hash(updates["password"])

        for field, value in updates.items():
            setattr(user, field, value)

        return await self.repo.update(user)

    async def delete(self, user_id: UUID):
        user = await self.get(user_id)
        await self.repo.delete(user)
