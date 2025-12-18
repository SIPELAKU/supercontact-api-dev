from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession

from app.repositories.department_repository import DepartmentRepository
from app.schemas.department_schema import DepartmentCreate, DepartmentUpdate
from app.models.department_model import Department


class DepartmentService:

    def __init__(self, db: AsyncSession):
        self.repo = DepartmentRepository(db)

    async def create_department(self, data: DepartmentCreate) -> Department:
        return await self.repo.create_with_branches(
            name=data.name,
            branch_names=data.branches,
        )

    async def get_departments(self):
        return await self.repo.get_all()

    async def get_department(self, department_id: UUID):
        return await self.repo.get_by_id(department_id)

    async def update_department(
        self,
        department_id: UUID,
        data: DepartmentUpdate,
    ) -> Department:
        return await self.repo.update(
            department_id=department_id,
            name=data.name,
            new_branches=data.branches,
        )

    async def delete_department(self, department_id: UUID):
        return await self.repo.delete(department_id)
