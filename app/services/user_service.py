from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.security import hash_password, verify_password, create_access_token
from app.repository.user_repository import UserRepository
from app.models.user_model import User, RoleEnum, StatusEnum
from app.schemas.user_schema import UserCreate, UserUpdate


class UserService:

    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def authenticate(self, email: str, password: str) -> User:
        user = await self.repo.get_by_email(email)

        if not user or not verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        return user

    def create_token(self, user: User) -> str:
        data = {
            "user_id": str(user.id),
            "email": user.email,
            "role": user.role.value,
        }
        return create_access_token(data)

    async def find_by_id(self, user_id: UUID):
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(404, "User not found")
        return user

    async def list_users(
        self,
        search: str | None,
        role: RoleEnum | None,
        status: StatusEnum | None,
        page: int,
        limit: int,
    ):
        skip = (page - 1) * limit

        users, total = await self.repo.list_users(
            search=search,
            role=role,
            status=status,
            skip=skip,
            limit=limit,
        )

        return {
            "items": users,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit,
        }

    async def create(self, req: UserCreate):
        existing = await self.repo.get_by_email(req.email)
        if existing:
            raise HTTPException(400, "Email already registered")

        avatar = req.fullname[:2].upper() if req.fullname else None

        user = User(
            fullname=req.fullname,
            email=req.email,
            password=hash_password(req.password),
            avatar_initial=avatar,
            role=req.role or RoleEnum.ADMIN,
            status=req.status or StatusEnum.active,
        )

        return await self.repo.create(user)

    async def update(self, user_id: UUID, req: UserUpdate):
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(404, "User not found")

        if req.email and req.email != user.email:
            if await self.repo.get_by_email(req.email):
                raise HTTPException(400, "Email already taken")
            user.email = req.email

        if req.fullname:
            user.fullname = req.fullname
            user.avatar_initial = req.fullname[:2].upper()

        if req.password:
            user.password = hash_password(req.password)

        if req.role:
            user.role = req.role

        if req.status:
            user.status = req.status

        return await self.repo.update(user)

    async def delete(self, user_id: UUID):
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(404, "User not found")

        await self.repo.delete(user)
        return {"message": "User deleted successfully"}
