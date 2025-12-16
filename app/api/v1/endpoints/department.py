from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.services.department_service import DepartmentService
from app.schemas.department_schema import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentReadWithRelations,
)
from app.utils.permissions import require_permissions

router = APIRouter(prefix="/department", tags=["Department"])


def get_department_service(
    db: AsyncSession = Depends(get_async_session),
) -> DepartmentService:
    return DepartmentService(db)


@router.post(
    "",
    response_model=DepartmentReadWithRelations,
    dependencies=[Depends(require_permissions("department:create"))],
)
async def create_department(
    data: DepartmentCreate,
    service: DepartmentService = Depends(get_department_service),
):
    dept = await service.create_department(data)
    return dept


@router.get(
    "",
    response_model=list[DepartmentReadWithRelations],
    dependencies=[Depends(require_permissions("department:read"))],
)
async def list_departments(
    service: DepartmentService = Depends(get_department_service),
):
    depts = await service.get_departments()
    return depts


@router.get(
    "/{department_id}",
    response_model=DepartmentReadWithRelations,
    dependencies=[Depends(require_permissions("department:read"))],
)
async def get_department(
    department_id: UUID,
    service: DepartmentService = Depends(get_department_service),
):
    dept = await service.get_department(department_id)
    return dept


@router.put(
    "/{department_id}",
    response_model=DepartmentReadWithRelations,
    dependencies=[Depends(require_permissions("department:update"))],
)
async def update_department(
    department_id: UUID,
    data: DepartmentUpdate,
    service: DepartmentService = Depends(get_department_service),
):
    updated = await service.update_department(department_id, data)
    return updated


@router.delete(
    "/{department_id}",
    dependencies=[Depends(require_permissions("department:delete"))],
)
async def delete_department(
    department_id: UUID,
    service: DepartmentService = Depends(get_department_service),
):
    await service.delete_department(department_id)
    return {"message": "Department deleted successfully"}
