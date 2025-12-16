from typing import Optional, List
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.exceptions import AppException
from app.models import User, UserStatus, UserLevel
from app.schemas import ErrorCode


class ManageUserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================
    # CREATE
    # ============================
    async def create_user(self, user: User) -> User:
        try:
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user

        except IntegrityError as e:
            await self.db.rollback()
            msg = str(e.orig).lower()

            if "user_id" in msg:
                raise AppException(ErrorCode.USER_ID_ALREADY_EXISTS)

            if "employee_id" in msg:
                raise AppException(ErrorCode.EMPLOYEE_ID_ALREADY_EXISTS)

            raise AppException(ErrorCode.DATABASE_ERROR)

    # ============================
    # GET
    # ============================
    async def get_user_by_id(self, id: UUID) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == id))
        return result.scalars().first()

    async def get_user_by_user_id(self, user_id: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.user_id == user_id))
        return result.scalars().first()

    async def get_user_by_employee_id(self, employee_id: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.employee_id == employee_id)
        )
        return result.scalars().first()

    # ============================
    # LIST
    # ============================
    async def list_users(self, skip: int = 0, limit: int = 50) -> List[User]:
        result = await self.db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()

    async def list_by_department(self, department_id: UUID) -> List[User]:
        result = await self.db.execute(
            select(User).where(User.department_id == department_id)
        )
        return result.scalars().all()

    async def list_by_branch(self, branch_id: UUID) -> List[User]:
        result = await self.db.execute(select(User).where(User.branch_id == branch_id))
        return result.scalars().all()

    async def list_by_role(self, role_id: UUID) -> List[User]:
        result = await self.db.execute(select(User).where(User.role_id == role_id))
        return result.scalars().all()

    async def list_by_status(self, status: UserStatus) -> List[User]:
        result = await self.db.execute(select(User).where(User.status == status))
        return result.scalars().all()

    async def list_managers(self) -> List[User]:
        result = await self.db.execute(
            select(User)
            .where(User.user_level == UserLevel.MANAGER)
            .order_by(User.created_at.asc())
        )
        return result.scalars().all()

    async def list_available_managers(self) -> List[User]:
        result = await self.db.execute(
            select(User)
            .where(User.user_level == UserLevel.MANAGER)
            .where(User.managed_department.is_(None))
            .order_by(User.created_at.asc())
        )
        return result.scalars().all()

    # ============================
    # UPDATE
    # ============================
    async def update_user(self, id: UUID, data: dict) -> User:
        user = await self.get_user_by_id(id)
        if not user:
            raise AppException(ErrorCode.USER_NOT_FOUND)

        if "status" in data and data["status"] is not None:
            try:
                data["status"] = UserStatus(data["status"])
            except ValueError:
                raise AppException(ErrorCode.INVALID_STATUS)

        if "user_level" in data and data["user_level"] is not None:
            try:
                data["user_level"] = UserLevel(data["user_level"])
            except ValueError:
                raise AppException(ErrorCode.INVALID_USER_LEVEL)

        allowed_fields = {
            "role_id",
            "department_id",
            "branch_id",
            "employee_id",
            "status",
            "user_level",
        }

        for key, value in data.items():
            if key in allowed_fields and value is not None:
                setattr(user, key, value)

        try:
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user

        except IntegrityError as e:
            await self.db.rollback()
            msg = str(e.orig).lower()

            if "employee_id" in msg:
                raise AppException(ErrorCode.EMPLOYEE_ID_ALREADY_EXISTS)

            raise AppException(ErrorCode.DATABASE_ERROR)

    # ============================
    # DELETE
    # ============================
    async def delete_user(self, id: UUID) -> bool:
        user = await self.get_user_by_id(id)
        if not user:
            raise AppException(ErrorCode.USER_NOT_FOUND)

        try:
            await self.db.delete(user)
            await self.db.commit()
            return True

        except IntegrityError:
            await self.db.rollback()
            raise AppException(ErrorCode.USER_CANNOT_BE_DELETED)
