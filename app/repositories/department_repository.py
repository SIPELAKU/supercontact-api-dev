from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import selectinload
from fastapi import status

from app.models.department_model import Department
from app.models.branch_model import Branch
from app.exceptions import AppException
from app.schemas.error_schema import ErrorCode


class DepartmentRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    # CREATE
    async def create_with_branches(
        self,
        name: str,
        branch_names: List[str],
    ) -> Department:

        if len(branch_names) != len(set(branch_names)):
            raise AppException(
                status_code=status.HTTP_400_BAD_REQUEST,
                code=ErrorCode.VALIDATION_ERROR,
                message="Duplicate branch names are not allowed",
            )

        dept = Department(name=name)

        try:
            self.db.add(dept)
            await self.db.flush()

            for branch_name in branch_names:
                self.db.add(
                    Branch(
                        name=branch_name,
                        department_id=dept.id,
                    )
                )

            await self.db.commit()

            result = await self.db.execute(
                select(Department)
                .where(Department.id == dept.id)
                .options(selectinload(Department.branches))
            )
            return result.scalar_one()

        except IntegrityError:
            await self.db.rollback()
            raise AppException(
                status_code=status.HTTP_409_CONFLICT,
                code=ErrorCode.ITEM_ALREADY_EXISTS,
                message="Department already exists",
            )

        except SQLAlchemyError as e:
            await self.db.rollback()
            raise AppException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                code=ErrorCode.DB_ERROR,
                message=str(e),
            )

    # READ
    async def get_all(self) -> List[Department]:
        result = await self.db.execute(
            select(Department).options(selectinload(Department.branches))
        )
        return result.scalars().all()

    async def get_by_id(self, department_id: UUID) -> Department:
        result = await self.db.execute(
            select(Department)
            .where(Department.id == department_id)
            .options(selectinload(Department.branches))
        )
        dept = result.scalar_one_or_none()

        if not dept:
            raise AppException(
                status_code=status.HTTP_404_NOT_FOUND,
                code=ErrorCode.DATA_NOT_FOUND,
                message="Department not found",
            )

        return dept

    # UPDATE
    async def update(
        self,
        department_id: UUID,
        name: Optional[str] = None,
        new_branches: Optional[List[str]] = None,
    ) -> Department:

        dept = await self.get_by_id(department_id)

        try:
            if name:
                dept.name = name

            if new_branches:
                existing = {b.name for b in dept.branches}

                for branch_name in new_branches:
                    if branch_name in existing:
                        raise AppException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            code=ErrorCode.VALIDATION_ERROR,
                            message=f"Branch '{branch_name}' already exists",
                        )

                    self.db.add(
                        Branch(
                            name=branch_name,
                            department_id=dept.id,
                        )
                    )

            await self.db.commit()

            result = await self.db.execute(
                select(Department)
                .where(Department.id == dept.id)
                .options(selectinload(Department.branches))
            )
            return result.scalar_one()

        except IntegrityError:
            await self.db.rollback()
            raise AppException(
                status_code=status.HTTP_409_CONFLICT,
                code=ErrorCode.ITEM_ALREADY_EXISTS,
                message="Duplicate data detected",
            )

        except SQLAlchemyError as e:
            await self.db.rollback()
            raise AppException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                code=ErrorCode.DB_ERROR,
                message=str(e),
            )

    # DELETE
    async def delete(self, department_id: UUID) -> bool:
        dept = await self.get_by_id(department_id)
        await self.db.delete(dept)
        await self.db.commit()
        return True
