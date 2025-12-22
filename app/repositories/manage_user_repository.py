from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy import or_, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession

from app.exceptions import AppException
from app.models.manage_user_model import (
    ManageUser,
    UserStatus,
    UserLevel,
)
from app.models.user_model import User
from app.models.branch_model import Branch
from app.models.department_enum import DepartmentEnum
from app.schemas.error_schema import ErrorCode


class ManageUserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # CREATE
    async def create(self, mu: ManageUser) -> ManageUser:
        try:
            self.db.add(mu)
            await self.db.commit()
            await self.db.refresh(mu)
            return mu
        except IntegrityError:
            await self.db.rollback()
            raise AppException(ErrorCode.DATABASE_ERROR)

    # GET
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

    # UPDATE
    async def update(self, mu: ManageUser) -> ManageUser:
        try:
            await self.db.commit()
            await self.db.refresh(mu)
            return mu
        except IntegrityError:
            await self.db.rollback()
            raise AppException(ErrorCode.DATABASE_ERROR)

    # SOFT DELETE
    async def soft_delete(self, mu: ManageUser):
        mu.status = UserStatus.INACTIVE
        await self.update(mu)

    # LIST
    async def list(
        self,
        *,
        page: int,
        limit: int,
        search: Optional[str],
        status: Optional[UserStatus],
        role_id: Optional[UUID],
    ) -> Tuple[int, List[ManageUser]]:
        stmt = (
            select(ManageUser)
            .join(User)
            .where(ManageUser.status != UserStatus.INACTIVE)
        )

        if search:
            stmt = stmt.where(
                or_(
                    User.fullname.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                    ManageUser.employee_id.ilike(f"%{search}%"),
                )
            )

        if status:
            stmt = stmt.where(ManageUser.status == status)

        if role_id:
            stmt = stmt.where(ManageUser.role_id == role_id)

        total = await self.db.scalar(select(func.count()).select_from(stmt.subquery()))

        result = await self.db.execute(stmt.offset((page - 1) * limit).limit(limit))

        return total, result.scalars().all()

    # FILTER BY DEPARTMENT
    async def get_active_users_by_department(
        self,
        *,
        department: DepartmentEnum,
        branch_id: Optional[UUID] = None,
        user_levels: Optional[List[UserLevel]] = None,
    ) -> List[ManageUser]:

        stmt = (
            select(ManageUser)
            .join(Branch)
            .join(User)
            .options(
                selectinload(ManageUser.user),
                selectinload(ManageUser.role),
                selectinload(ManageUser.branch),
            )
            .where(
                Branch.department == department,
                ManageUser.status == UserStatus.ACTIVE,
            )
        )

        if branch_id:
            stmt = stmt.where(ManageUser.branch_id == branch_id)

        if user_levels:
            stmt = stmt.where(ManageUser.user_level.in_(user_levels))

        result = await self.db.execute(stmt.order_by(User.fullname))
        return result.scalars().all()

    # HARD DELETE
    async def hard_delete(self, mu: ManageUser):
        try:
            await self.db.delete(mu)
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise AppException(ErrorCode.DATABASE_ERROR)
