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
from app.models.manage_user_model import UserStatus

router = APIRouter(
    prefix="/departments",
    tags=["Departments"],
)


# CREATE BRANCH
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


# READ
@router.get(
    "/branches",
    response_model=List[BranchRead],
)
async def get_branches(
    department: Optional[DepartmentEnum] = Query(None),
    q: Optional[str] = Query(None, min_length=2),
    db: AsyncSession = Depends(get_async_session),
):
    service = DepartmentService(db)
    return await service.get_branches(
        department=department,
        keyword=q,
    )


# READ BY ID
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


# UPDATE
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


# DELETE
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


# DEPARTMENT DETAIL
@router.get(
    "/{department}/detail",
)
async def get_department_detail(
    department: DepartmentEnum,
    branch_id: Optional[UUID] = Query(None),
    search: Optional[str] = Query(None, min_length=2),
    status: Optional[UserStatus] = Query(None),
    db: AsyncSession = Depends(get_async_session),
):
    service = DepartmentDetailService(db)
    return await service.get_detail(
        department=department,
        branch_id=branch_id,
        search=search,
        status=status,
    )
