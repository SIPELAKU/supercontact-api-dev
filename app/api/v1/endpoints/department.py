from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_async_session
from app.services.department_service import DepartmentService
from app.schemas.department_schema import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentReadWithRelations,
)

router = APIRouter(
    prefix="/departments",
    tags=["Departments"],
)


# =========================
# CREATE DEPARTMENT
# =========================
@router.post(
    "",
    response_model=DepartmentReadWithRelations,
    status_code=status.HTTP_201_CREATED,
)
async def create_department(
    payload: DepartmentCreate,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Create department + optional branches

    Example payload:
    {
        "name": "Sales",
        "branches": ["Jakarta", "Bandung"]
    }
    """
    service = DepartmentService(db)
    return await service.create_department(payload)


# =========================
# GET ALL DEPARTMENTS
# =========================
@router.get(
    "",
    response_model=List[DepartmentReadWithRelations],
)
async def get_departments(
    db: AsyncSession = Depends(get_async_session),
):
    """
    Get all departments with branches
    """
    service = DepartmentService(db)
    return await service.get_departments()


# =========================
# GET DEPARTMENT BY ID
# =========================
@router.get(
    "/{department_id}",
    response_model=DepartmentReadWithRelations,
)
async def get_department(
    department_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Get single department with branches
    """
    service = DepartmentService(db)
    return await service.get_department(department_id)


# =========================
# UPDATE DEPARTMENT
# =========================
@router.put(
    "/{department_id}",
    response_model=DepartmentReadWithRelations,
)
async def update_department(
    department_id: UUID,
    payload: DepartmentUpdate,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Update department name and/or add new branches

    Example payload:
    {
        "name": "Sales",
        "branches": ["Surabaya", "Medan"]
    }
    """
    service = DepartmentService(db)
    return await service.update_department(
        department_id=department_id,
        data=payload,
    )


# =========================
# DELETE DEPARTMENT
# =========================
@router.delete(
    "/{department_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_department(
    department_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Delete department (branches auto deleted via cascade)
    """
    service = DepartmentService(db)
    await service.delete_department(department_id)
