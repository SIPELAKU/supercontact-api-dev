from uuid import UUID
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from app.models.branch_model import Branch
from app.models.department_enum import DepartmentEnum
from app.schemas.branch_schema import BranchCreate, BranchUpdate
from app.exceptions import AppException
from app.schemas.error_schema import ErrorCode


class DepartmentRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # =========================
    # CREATE
    # =========================
    async def add_branch(self, data: BranchCreate) -> Branch:
        branch = Branch(
            department=data.department,
            name=data.branch.strip(),
        )

        try:
            self.db.add(branch)
            await self.db.commit()
            await self.db.refresh(branch)
            return branch

        except IntegrityError:
            await self.db.rollback()
            raise AppException(
                status_code=status.HTTP_409_CONFLICT,
                code=ErrorCode.ITEM_ALREADY_EXISTS,
                message=(
                    f"Branch '{data.branch}' already exists "
                    f"in department '{data.department.value}'"
                ),
            )

        except SQLAlchemyError as e:
            await self.db.rollback()
            raise AppException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                code=ErrorCode.DB_ERROR,
                message=str(e),
            )

    # =========================
    # GET ALL + FILTER + SEARCH (🔥)
    # =========================
    async def get_branches(
        self,
        *,
        department: Optional[DepartmentEnum] = None,
        keyword: Optional[str] = None,
    ) -> list[Branch]:

        stmt = select(Branch)

        if department:
            stmt = stmt.where(Branch.department == department)

        if keyword:
            stmt = stmt.where(func.lower(Branch.name).ilike(f"%{keyword.lower()}%"))

        stmt = stmt.order_by(Branch.department, Branch.name)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    # =========================
    # GET BY ID
    # =========================
    async def get_branch_by_id(self, branch_id: UUID) -> Branch:
        branch = await self.db.get(Branch, branch_id)
        if not branch:
            raise AppException(
                status_code=status.HTTP_404_NOT_FOUND,
                code=ErrorCode.DATA_NOT_FOUND,
                message="Branch not found",
            )
        return branch

    # =========================
    # UPDATE
    # =========================
    async def update_branch(self, branch_id: UUID, data: BranchUpdate) -> Branch:
        branch = await self.get_branch_by_id(branch_id)

        if data.branch is not None:
            branch.name = data.branch.strip()

        if data.department is not None:
            branch.department = data.department

        try:
            await self.db.commit()
            await self.db.refresh(branch)
            return branch

        except IntegrityError:
            await self.db.rollback()
            raise AppException(
                status_code=status.HTTP_409_CONFLICT,
                code=ErrorCode.ITEM_ALREADY_EXISTS,
                message=(
                    f"Branch '{branch.name}' already exists "
                    f"in department '{branch.department.value}'"
                ),
            )

    # =========================
    # DELETE
    # =========================
    async def delete_branch(self, branch_id: UUID):
        branch = await self.get_branch_by_id(branch_id)
        await self.db.delete(branch)
        await self.db.commit()
