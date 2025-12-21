from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_async_session
from app.services.department_service import DepartmentService
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


# CREATE
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


# GET ALL
@router.get(
    "/branches",
    response_model=List[BranchRead],
)
async def get_all_branches(
    db: AsyncSession = Depends(get_async_session),
):
    service = DepartmentService(db)
    return await service.get_all_branches()


# GET BY ID
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


# DELETE BRANCH
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


# GET BRANCHES BY DEPARTMENT
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


# FILTER BRANCH BY NAME
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


# DEPARTMENT DETAIL
@router.get(
    "/branches/{branch_id}/detail",
)
async def get_department_detail(
    branch_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    service = DepartmentService(db)
    return await service.get_department_detail(branch_id)
