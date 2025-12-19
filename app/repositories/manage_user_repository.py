from typing import Optional, List
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.exceptions import AppException
from app.models import (
    ManageUser,
    UserStatus,
    UserLevel,
    Position,
    User,
)
from app.schemas import ErrorCode


class ManageUserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # CREATE
    async def create(self, manage_user: ManageUser) -> ManageUser:
        try:
            self.db.add(manage_user)
            await self.db.commit()
            await self.db.refresh(manage_user)
            return manage_user

        except IntegrityError as e:
            await self.db.rollback()
            msg = str(e.orig).lower()

            if "user_id" in msg:
                raise AppException(ErrorCode.USER_ALREADY_ASSIGNED)

            if "employee_id" in msg:
                raise AppException(ErrorCode.EMPLOYEE_ID_ALREADY_EXISTS)

            raise AppException(ErrorCode.DATABASE_ERROR)

    async def get_by_id(self, id: UUID) -> Optional[ManageUser]:
        result = await self.db.execute(select(ManageUser).where(ManageUser.id == id))
        return result.scalars().first()

    async def get_by_user_id(self, user_id: UUID) -> Optional[ManageUser]:
        result = await self.db.execute(
            select(ManageUser).where(ManageUser.user_id == user_id)
        )
        return result.scalars().first()

    async def get_by_employee_id(self, employee_id: str) -> Optional[ManageUser]:
        result = await self.db.execute(
            select(ManageUser).where(ManageUser.employee_id == employee_id)
        )
        return result.scalars().first()

    async def get_by_user_email(self, email: str) -> Optional[ManageUser]:
        result = await self.db.execute(
            select(ManageUser)
            .join(User, User.id == ManageUser.user_id)
            .where(User.email == email)
        )
        return result.scalars().first()

    # LIST
    async def list(self, skip: int = 0, limit: int = 50) -> List[ManageUser]:
        result = await self.db.execute(
            select(ManageUser)
            .offset(skip)
            .limit(limit)
            .order_by(ManageUser.created_at.asc())
        )
        return result.scalars().all()

    async def list_by_department(self, department_id: UUID) -> List[ManageUser]:
        result = await self.db.execute(
            select(ManageUser)
            .where(ManageUser.department_id == department_id)
            .order_by(ManageUser.created_at.asc())
        )
        return result.scalars().all()

    async def list_by_branch(self, branch_id: UUID) -> List[ManageUser]:
        result = await self.db.execute(
            select(ManageUser)
            .where(ManageUser.branch_id == branch_id)
            .order_by(ManageUser.created_at.asc())
        )
        return result.scalars().all()

    async def list_by_department_and_branch(
        self,
        department_id: UUID,
        branch_id: UUID,
    ) -> List[ManageUser]:
        result = await self.db.execute(
            select(ManageUser)
            .where(
                ManageUser.department_id == department_id,
                ManageUser.branch_id == branch_id,
            )
            .order_by(ManageUser.created_at.asc())
        )
        return result.scalars().all()

    async def list_by_role(self, role_id: UUID) -> List[ManageUser]:
        result = await self.db.execute(
            select(ManageUser)
            .where(ManageUser.role_id == role_id)
            .order_by(ManageUser.created_at.asc())
        )
        return result.scalars().all()

    async def list_by_status(self, status: UserStatus) -> List[ManageUser]:
        result = await self.db.execute(
            select(ManageUser)
            .where(ManageUser.status == status)
            .order_by(ManageUser.created_at.asc())
        )
        return result.scalars().all()

    async def list_by_user_level(self, user_level: UserLevel) -> List[ManageUser]:
        result = await self.db.execute(
            select(ManageUser)
            .where(ManageUser.user_level == user_level)
            .order_by(ManageUser.created_at.asc())
        )
        return result.scalars().all()

    async def list_managers(self) -> List[ManageUser]:
        return await self.list_by_user_level(UserLevel.MANAGER)

    async def list_supervisors(self) -> List[ManageUser]:
        return await self.list_by_user_level(UserLevel.SUPERVISOR)

    async def list_active(self) -> List[ManageUser]:
        result = await self.db.execute(
            select(ManageUser)
            .where(ManageUser.status == UserStatus.ACTIVE)
            .order_by(ManageUser.created_at.asc())
        )
        return result.scalars().all()

    # UPDATE
    async def update(self, id: UUID, data: dict) -> ManageUser:
        manage_user = await self.get_by_id(id)
        if not manage_user:
            raise AppException(ErrorCode.MANAGE_USER_NOT_FOUND)

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

        if "position" in data and data["position"] is not None:
            try:
                data["position"] = Position(data["position"])
            except ValueError:
                raise AppException(ErrorCode.INVALID_POSITION)

        allowed_fields = {
            "department_id",
            "branch_id",
            "role_id",
            "employee_id",
            "status",
            "user_level",
            "position",
        }

        for key, value in data.items():
            if key in allowed_fields:
                setattr(manage_user, key, value)

        try:
            self.db.add(manage_user)
            await self.db.commit()
            await self.db.refresh(manage_user)
            return manage_user

        except IntegrityError as e:
            await self.db.rollback()
            msg = str(e.orig).lower()

            if "employee_id" in msg:
                raise AppException(ErrorCode.EMPLOYEE_ID_ALREADY_EXISTS)

            raise AppException(ErrorCode.DATABASE_ERROR)

    # DELETE
    async def delete(self, id: UUID) -> bool:
        manage_user = await self.get_by_id(id)
        if not manage_user:
            raise AppException(ErrorCode.MANAGE_USER_NOT_FOUND)

        try:
            await self.db.delete(manage_user)
            await self.db.commit()
            return True

        except IntegrityError:
            await self.db.rollback()
            raise AppException(ErrorCode.MANAGE_USER_CANNOT_BE_DELETED)
