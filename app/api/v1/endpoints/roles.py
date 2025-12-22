from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.services.role_service import RoleService
from app.schemas.role_schema import RoleCreate, RoleRead
from app.utils.permissions import require_permissions

router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
)


# CREATE ROLE
@router.post(
    "",
    response_model=RoleRead,
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(require_permissions("role:create"))],
)
async def create_role(
    payload: RoleCreate,
    db: AsyncSession = Depends(get_async_session),
):
    service = RoleService(db)
    return await service.create(payload.role_name)


# LIST ROLES
@router.get(
    "",
    response_model=List[RoleRead],
    # dependencies=[Depends(require_permissions("role:view"))],
)
async def list_roles(
    db: AsyncSession = Depends(get_async_session),
):
    service = RoleService(db)
    return await service.get_all()
