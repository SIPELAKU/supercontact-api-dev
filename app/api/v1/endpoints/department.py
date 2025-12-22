from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_async_session
from app.services.department_service import DepartmentService
from app.services.department_detail_service import DepartmentDetailService
from app.schemas.branch_schema import (
    BranchCreate,
    BranchUpdate,
    BranchRead,
)
from app.models.department_enum import DepartmentEnum

router = APIRouter(
    prefix="/departments",
    tags=["Departments"],
)

# =========================
# BRANCH CRUD
# =========================


@router.post(
    "/branches",
    response_model=BranchRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_branch(
    payload: BranchCreate,
    db: AsyncSession = Depends(get_async_session),
):
    service = DepartmentService(db)
    return await service.add_branch(payload)


@router.get(
    "/branches",
    response_model=List[BranchRead],
)
async def get_all_branches(
    db: AsyncSession = Depends(get_async_session),
):
    service = DepartmentService(db)
    return await service.get_all_branches()


@router.get(
    "/branches/{branch_id}",
    response_model=BranchRead,
)
async def get_branch_by_id(
    branch_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    service = DepartmentService(db)
    return await service.get_branch_by_id(branch_id)


@router.put(
    "/branches/{branch_id}",
    response_model=BranchRead,
)
async def update_branch(
    branch_id: UUID,
    payload: BranchUpdate,
    db: AsyncSession = Depends(get_async_session),
):
    service = DepartmentService(db)
    return await service.update_branch(branch_id, payload)


@router.delete(
    "/branches/{branch_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_branch(
    branch_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    service = DepartmentService(db)
    await service.delete_branch(branch_id)


# =========================
# FILTER & GROUPING
# =========================


@router.get(
    "/{department}/branches",
    response_model=List[BranchRead],
)
async def get_branches_by_department(
    department: DepartmentEnum,
    db: AsyncSession = Depends(get_async_session),
):
    service = DepartmentService(db)
    return await service.get_branches_by_department(department)


@router.get(
    "/branches/search",
    response_model=List[BranchRead],
)
async def filter_branch(
    q: str = Query(..., min_length=2),
    db: AsyncSession = Depends(get_async_session),
):
    service = DepartmentService(db)
    return await service.filter_branch(q)


# =========================
# DEPARTMENT DETAIL (FIXED)
# =========================


@router.get(
    "/{department}/detail",
)
async def get_department_detail(
    department: DepartmentEnum,
    branch_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Department Detail Page

    - Filter by Department
    - Optional filter by Branch
    - ONLY ACTIVE STAFF
    - Query langsung ke database (no in-memory filtering)
    """

    service = DepartmentDetailService(db)

    return await service.get_detail(
        department=department,
        branch_id=branch_id,
    )
