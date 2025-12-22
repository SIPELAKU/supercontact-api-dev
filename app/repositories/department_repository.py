from uuid import UUID

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

    # CREATE
    async def add_branch(self, data: BranchCreate) -> Branch:
        branch = Branch(
            department=data.department,
            name=data.name.strip(),
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
                    f"Branch '{data.name}' already exists "
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

    # GET ALL
    async def get_all_branches(self) -> list[Branch]:
        result = await self.db.execute(
            select(Branch).order_by(Branch.department, Branch.name)
        )
        return result.scalars().all()

    # GET BY ID
    async def get_branch_by_id(self, branch_id: UUID) -> Branch:
        branch = await self.db.get(Branch, branch_id)
        if not branch:
            raise AppException(
                status_code=status.HTTP_404_NOT_FOUND,
                code=ErrorCode.DATA_NOT_FOUND,
                message="Branch not found",
            )
        return branch

    # UPDATE
    async def update_branch(self, branch_id: UUID, data: BranchUpdate) -> Branch:
        branch = await self.get_branch_by_id(branch_id)

        if data.name is not None:
            branch.name = data.name.strip()

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

        except SQLAlchemyError as e:
            await self.db.rollback()
            raise AppException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                code=ErrorCode.DB_ERROR,
                message=str(e),
            )

    # DELETE
    async def delete_branch(self, branch_id: UUID):
        branch = await self.get_branch_by_id(branch_id)

        try:
            await self.db.delete(branch)
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise AppException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                code=ErrorCode.DB_ERROR,
                message=str(e),
            )

    async def branch_exists(
        self,
        department: DepartmentEnum,
        name: str,
    ) -> bool:
        result = await self.db.execute(
            select(func.count(Branch.id)).where(
                Branch.department == department,
                func.lower(Branch.name) == name.lower(),
            )
        )
        return result.scalar_one() > 0

    # FILTER BY DEPARTMENT
    async def get_branches_by_department(
        self,
        department: DepartmentEnum,
    ) -> list[Branch]:
        result = await self.db.execute(
            select(Branch).where(Branch.department == department).order_by(Branch.name)
        )
        return result.scalars().all()

    # FILTER BY NAME
    async def filter_branch(self, keyword: str) -> list[Branch]:
        result = await self.db.execute(
            select(Branch)
            .where(func.lower(Branch.name).ilike(f"%{keyword.lower()}%"))
            .order_by(Branch.department, Branch.name)
        )
        return result.scalars().all()

    async def get_department_branch_by_id(
        self,
        department: DepartmentEnum,
        branch_id: UUID,
    ) -> Branch:
        result = await self.db.execute(
            select(Branch).where(
                Branch.id == branch_id,
                Branch.department == department,
            )
        )
        branch = result.scalars().first()
        if not branch:
            raise AppException(
                status_code=status.HTTP_404_NOT_FOUND,
                code=ErrorCode.DATA_NOT_FOUND,
                message="Branch not found in this department",
            )
        return branch

    async def get_department_branch_by_name(
        self,
        department: DepartmentEnum,
        branch_name: str,
    ) -> Branch:
        result = await self.db.execute(
            select(Branch).where(
                Branch.department == department,
                func.lower(Branch.name) == branch_name.lower(),
            )
        )
        branch = result.scalars().first()
        if not branch:
            raise AppException(
                status_code=status.HTTP_404_NOT_FOUND,
                code=ErrorCode.DATA_NOT_FOUND,
                message="Branch not found in this department",
            )
        return branch
