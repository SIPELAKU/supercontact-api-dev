from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession

from app.repositories.department_repository import DepartmentRepository
from app.schemas.branch_schema import BranchCreate, BranchUpdate
from app.models.department_enum import DepartmentEnum
from app.models.branch_model import Branch


class DepartmentService:
    def __init__(self, db: AsyncSession):
        self.repo = DepartmentRepository(db)

    # CREATE
    async def add_branch(self, data: BranchCreate) -> Branch:
        return await self.repo.add_branch(data)

    # READ
    async def get_all_branches(self) -> list[Branch]:
        return await self.repo.get_all_branches()

    async def get_branch_by_id(self, branch_id: UUID) -> Branch:
        return await self.repo.get_branch_by_id(branch_id)

    async def get_branches_by_department(
        self,
        department: DepartmentEnum,
    ) -> list[Branch]:
        return await self.repo.get_branches_by_department(department)

    # UPDATE
    async def update_branch(
        self,
        branch_id: UUID,
        data: BranchUpdate,
    ) -> Branch:
        return await self.repo.update_branch(branch_id, data)

    # DELETE
    async def delete_branch(self, branch_id: UUID) -> None:
        await self.repo.delete_branch(branch_id)

    # FILTER
    async def filter_branch(self, keyword: str) -> list[Branch]:
        return await self.repo.filter_branch(keyword)

    async def branch_exists(
        self,
        department: DepartmentEnum,
        name: str,
    ) -> bool:
        return await self.repo.branch_exists(department, name)

    async def get_department_branch_by_id(
        self,
        *,
        department: DepartmentEnum,
        branch_id: UUID,
    ) -> Branch:

        return await self.repo.get_department_branch_by_id(
            department=department,
            branch_id=branch_id,
        )

    async def get_department_branch_by_name(
        self,
        *,
        department: DepartmentEnum,
        branch_name: str,
    ) -> Branch:

        return await self.repo.get_department_branch_by_name(
            department=department,
            branch_name=branch_name,
        )
