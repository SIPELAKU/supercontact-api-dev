from uuid import UUID
from typing import Optional

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

    # =========================
    # MAPPER
    # =========================
    def _to_branch_read(self, branch: Branch) -> BranchRead:
        return BranchRead(
            id=branch.id,
            department=branch.department,
            branch=branch.name,
        )

    # =========================
    # CREATE
    # =========================
    async def add_branch(self, data: BranchCreate) -> BranchRead:
        branch = await self.repo.add_branch(data)
        return self._to_branch_read(branch)

    # =========================
    # READ (ALL / FILTER / SEARCH)
    # =========================
    async def get_branches(
        self,
        *,
        department: Optional[DepartmentEnum] = None,
        keyword: Optional[str] = None,
    ) -> list[BranchRead]:
        branches = await self.repo.get_branches(
            department=department,
            keyword=keyword,
        )
        return [self._to_branch_read(b) for b in branches]

    # =========================
    # READ BY ID
    # =========================
    async def get_branch_by_id(self, branch_id: UUID) -> BranchRead:
        branch = await self.repo.get_branch_by_id(branch_id)
        return self._to_branch_read(branch)

    # =========================
    # UPDATE
    # =========================
    async def update_branch(
        self,
        branch_id: UUID,
        data: BranchUpdate,
    ) -> BranchRead:
        branch = await self.repo.update_branch(branch_id, data)
        return self._to_branch_read(branch)

    # =========================
    # DELETE
    # =========================
    async def delete_branch(self, branch_id: UUID) -> None:
        await self.repo.delete_branch(branch_id)
