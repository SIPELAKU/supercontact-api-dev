from uuid import UUID

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import hash_password, verify_password
from app.exceptions import AppException
from app.models import User, UserRole, UserStatus
from app.repositories import UserRepository
from app.schemas import UserCreateRequest, UserUpdateRequest
from app.schemas import UserGetQuery, ErrorCode


class UserService:

    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def authenticate(self, email: EmailStr, password: str) -> User:
        user = await self.repo.get_by_email(email)

        if not user or not verify_password(password, user.password):
            raise AppException(
                code=ErrorCode.AUTH_REQUIRED,
                status_code=401,
                message="Invalid email or password",
            )

        return user

    async def find_by_id(self, user_id: UUID):
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise AppException(
                code=ErrorCode.NOT_FOUND, status_code=404, message="User not found"
            )
        return user

    async def find_all_users(
        self,
        query_params: UserGetQuery,
    ):

        users, total = await self.repo.list_users(query_params=query_params)

        return {
            "users": users,
            "total": total,
            "page": query_params.page,
            "limit": query_params.limit,
            "total_pages": (total + query_params.limit - 1) // query_params.limit,
        }

    async def create(self, req: UserCreateRequest):
        existing = await self.repo.get_by_email(req.email)
        if existing:
            raise AppException(
                status_code=400,
                code=ErrorCode.VALIDATION_ERROR,
                message="Email already registered",
            )

        avatar = req.fullname[:2].upper() if req.fullname else None

        user = User(
            fullname=req.fullname,
            email=req.email,
            password=hash_password(req.password),
            avatar_initial=avatar,
            role=req.role or UserRole.ADMIN,
            status=req.status or UserStatus.ACTIVE,
        )

        return await self.repo.create(user)

    async def update(self, user_id: UUID, req: UserUpdateRequest):
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise AppException(
                status_code=404, code=ErrorCode.NOT_FOUND, message="User not found"
            )

        if req.email and req.email != user.email:
            if await self.repo.get_by_email(req.email):
                raise AppException(
                    status_code=400,
                    code=ErrorCode.VALIDATION_ERROR,
                    message="Email already taken",
                )
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
            raise AppException(
                status_code=404, code=ErrorCode.NOT_FOUND, message="User not found"
            )

        await self.repo.delete(user)
        return {"message": "User deleted successfully"}
