from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from uuid import UUID

from app.core.security import hash_password, verify_password, create_access_token
from app.repository.user_repository import UserRepository
from app.models.user_model import User, RoleEnum, StatusEnum
from app.schemas.user_schema import UserCreate, UserUpdate


class UserService:

    def __init__(self, repo: UserRepository | None = None):
        self.repo = repo or UserRepository()

    # --------------------------
    # AUTH
    # --------------------------
    async def authenticate(self, db: AsyncSession, email: str, password: str) -> User:
        user = await self.repo.get_by_email(db, email)

        if not user or not verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        return user

    def create_token(self, user: User) -> str:
        data = {
            "user_id": str(user.id),
            "email": user.email,
            "role": user.role.value,  # Enum → string
        }
        return create_access_token(data)

    # --------------------------
    # CRUD
    # --------------------------
    async def get_all(self, db: AsyncSession):
        result = await db.exec(select(User))
        return result.scalars().all()

    async def find_by_id(self, db: AsyncSession, user_id: UUID):
        user = await self.repo.get_by_id(db, user_id)
        if not user:
            raise HTTPException(404, "User not found")
        return user

    async def list_users(self, db: AsyncSession, search, role, status, page, page_size):
        skip = (page - 1) * page_size

        users, total = await self.repo.list_users(
            db, search, role, status, skip, page_size
        )

        return {"data": users, "total": total, "page": page, "page_size": page_size}

    async def create(self, db: AsyncSession, req: UserCreate):
        existing = await self.repo.get_by_email(db, req.email)
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

        return await self.repo.create(db, user)

    async def update(self, db: AsyncSession, user_id: UUID, req: UserUpdate):
        user = await self.repo.get_by_id(db, user_id)
        if not user:
            raise HTTPException(404, "User not found")

        if req.email and req.email != user.email:
            if await self.repo.get_by_email(db, req.email):
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

        return await self.repo.update(db, user)

    async def delete(self, db: AsyncSession, user_id: UUID):
        user = await self.repo.get_by_id(db, user_id)
        if not user:
            raise HTTPException(404, "User not found")

        await self.repo.delete(db, user)
        return {"message": "User deleted successfully"}
