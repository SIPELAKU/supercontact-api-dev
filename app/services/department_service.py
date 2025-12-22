from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession

from app.repositories.department_repository import DepartmentRepository
from app.schemas.branch_schema import (
    BranchCreate,
    BranchUpdate,
    BranchRead,
)
from app.models.department_enum import DepartmentEnum
from app.models.branch_model import Branch


class DepartmentService:
    def __init__(self, db: AsyncSession):
        self.repo = DepartmentRepository(db)

    def _to_branch_read(self, branch: Branch) -> BranchRead:
        return BranchRead(
            id=branch.id,
            department=branch.department,
            branch=branch.name,
        )

    # CREATE
    async def add_branch(self, data: BranchCreate) -> BranchRead:
        branch = await self.repo.add_branch(data)
        return self._to_branch_read(branch)

    # READ
    async def get_all_branches(self) -> list[BranchRead]:
        branches = await self.repo.get_all_branches()
        return [self._to_branch_read(b) for b in branches]

    async def get_branch_by_id(self, branch_id: UUID) -> BranchRead:
        branch = await self.repo.get_branch_by_id(branch_id)
        return self._to_branch_read(branch)

    async def get_branches_by_department(
        self,
        department: DepartmentEnum,
    ) -> list[BranchRead]:
        branches = await self.repo.get_branches_by_department(department)
        return [self._to_branch_read(b) for b in branches]

    # UPDATE
    async def update_branch(
        self,
        branch_id: UUID,
        data: BranchUpdate,
    ) -> BranchRead:
        branch = await self.repo.update_branch(branch_id, data)
        return self._to_branch_read(branch)

    # DELETE
    async def delete_branch(self, branch_id: UUID) -> None:
        await self.repo.delete_branch(branch_id)

    # FILTER
    async def filter_branch(self, keyword: str) -> list[BranchRead]:
        branches = await self.repo.filter_branch(keyword)
        return [self._to_branch_read(b) for b in branches]

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
    ) -> BranchRead:
        branch = await self.repo.get_department_branch_by_id(
            department=department,
            branch_id=branch_id,
        )
        return self._to_branch_read(branch)

    async def get_department_branch_by_name(
        self,
        *,
        department: DepartmentEnum,
        branch_name: str,
    ) -> BranchRead:
        branch = await self.repo.get_department_branch_by_name(
            department=department,
            branch_name=branch_name,
        )
        return self._to_branch_read(branch)
