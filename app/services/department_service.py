from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession

from app.repositories.department_repository import DepartmentRepository
from app.schemas.branch_schema import BranchCreate, BranchUpdate
from app.models.department_enum import DepartmentEnum


class DepartmentService:

    def __init__(self, db: AsyncSession):
        self.repo = DepartmentRepository(db)

    async def add_branch(self, data: BranchCreate):
        return await self.repo.add_branch(data)

    async def get_all_branches(self):
        return await self.repo.get_all_branches()

    async def get_branch_by_id(self, branch_id: UUID):
        return await self.repo.get_branch_by_id(branch_id)

    async def update_branch(self, branch_id: UUID, data: BranchUpdate):
        return await self.repo.update_branch(branch_id, data)

    async def branch_exists(self, department: DepartmentEnum, name: str):
        return await self.repo.branch_exists(department, name)

    async def get_branches_by_department(self, department: DepartmentEnum):
        return await self.repo.get_branches_by_department(department)

    async def filter_branch(self, keyword: str):
        return await self.repo.filter_branch(keyword)

    async def get_department_detail(self, branch_id: UUID):
        return await self.repo.get_department_detail(branch_id)

    async def delete_branch(self, branch_id: UUID):
        return await self.repo.delete_branch(branch_id)
