from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from app.models.department_model import Department, DepartmentName
from app.models.branch_model import Branch
from app.models.user_model import User
from app.exceptions import AppException
from app.schemas.error_schema import ErrorCode


class DepartmentRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_user(self, user_id: UUID) -> User:
        user = await self.db.get(User, user_id)
        if not user:
            raise AppException(ErrorCode.DATA_NOT_FOUND, "User not found")
        return user

    async def create_with_branches(
        self,
        name: DepartmentName,
        branch_names: List[str],
        manager_id: Optional[UUID] = None,
    ) -> Department:

        exists = await self.db.scalar(select(Department).where(Department.name == name))
        if exists:
            raise AppException(
                ErrorCode.ITEM_ALREADY_EXISTS, "Department name already exists"
            )

        if len(branch_names) != len(set(branch_names)):
            raise AppException(
                ErrorCode.VALIDATION_ERROR, "Duplicate branch names are not allowed"
            )

        # Validate manager
        if manager_id:
            await self._get_user(manager_id)

            used = await self.db.scalar(
                select(Department).where(Department.manager_id == manager_id)
            )
            if used:
                raise AppException(
                    ErrorCode.BAD_REQUEST,
                    "This user already manages another department",
                )

        dept = Department(name=name, manager_id=manager_id)

        try:
            self.db.add(dept)
            await self.db.flush()

            # Create branches
            for bname in branch_names:
                self.db.add(Branch(name=bname, department_id=dept.id))

            await self.db.commit()
            await self.db.refresh(dept)

            return dept

        except SQLAlchemyError as e:
            await self.db.rollback()
            raise AppException(ErrorCode.DB_ERROR, str(e))

    async def get_all(self) -> List[Department]:
        result = await self.db.execute(
            select(Department).options(selectinload(Department.branches))
        )
        return result.scalars().all()

    async def get_by_id(self, department_id: UUID) -> Department:
        dept = await self.db.get(Department, department_id)
        if not dept:
            raise AppException(ErrorCode.DATA_NOT_FOUND, "Department not found")
        return dept

    async def update(
        self,
        department_id: UUID,
        name: Optional[DepartmentName] = None,
        manager_id: Optional[UUID] = None,
        new_branches: Optional[List[str]] = None,
    ) -> Department:

        dept = await self.get_by_id(department_id)

        # Update department name
        if name and name != dept.name:
            exists = await self.db.scalar(
                select(Department).where(Department.name == name)
            )
            if exists:
                raise AppException(
                    ErrorCode.ITEM_ALREADY_EXISTS, "Department name already exists"
                )
            dept.name = name

        if manager_id is not None:
            if manager_id:
                await self._get_user(manager_id)
                used = await self.db.scalar(
                    select(Department).where(Department.manager_id == manager_id)
                )
                if used:
                    raise AppException(
                        ErrorCode.BAD_REQUEST,
                        "Manager already leads another department",
                    )
                dept.manager_id = manager_id
            else:
                dept.manager_id = None

        if new_branches:
            existing = {b.name for b in dept.branches}

            for bname in new_branches:
                if bname in existing:
                    raise AppException(
                        ErrorCode.VALIDATION_ERROR, f"Branch '{bname}' already exists"
                    )
                self.db.add(Branch(name=bname, department_id=dept.id))

        await self.db.commit()
        await self.db.refresh(dept)
        return dept

    async def delete(self, department_id: UUID) -> bool:
        dept = await self.get_by_id(department_id)
        await self.db.delete(dept)
        await self.db.commit()
        return True
