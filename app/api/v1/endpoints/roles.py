from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.session import get_async_session
from app.models.role_model import Role, Permission, RolePermission
from app.exceptions import AppException
from app.schemas import ErrorCode

router = APIRouter()


@router.post("", response_model=Role)
async def create_role(role: Role, db: AsyncSession = Depends(get_async_session)):
    exists = await db.execute(select(Role).where(Role.role_name == role.role_name))
    if exists.scalar_one_or_none():
        raise AppException(
            status_code=400,
            code=ErrorCode.BAD_REQUEST,
            message="Role already exists",
        )

    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


@router.get("", response_model=list[Role])
async def list_roles(db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(Role))
    return result.scalars().all()


@router.get("/{role_id}", response_model=Role)
async def get_role(role_id: UUID, db: AsyncSession = Depends(get_async_session)):
    role = await db.get(Role, role_id)
    if not role:
        raise AppException(404, ErrorCode.NOT_FOUND, "Role not found")
    return role


@router.delete("/{role_id}")
async def delete_role(role_id: UUID, db: AsyncSession = Depends(get_async_session)):
    role = await db.get(Role, role_id)
    if not role:
        raise AppException(404, ErrorCode.NOT_FOUND, "Role not found")

    await db.delete(role)
    await db.commit()
    return {"message": "Role deleted"}


@router.post("/permissions", response_model=Permission)
async def create_permission(
    permission: Permission, db: AsyncSession = Depends(get_async_session)
):
    exists = await db.execute(
        select(Permission).where(
            Permission.permission_name == permission.permission_name
        )
    )
    if exists.scalar_one_or_none():
        raise AppException(400, ErrorCode.BAD_REQUEST, "Permission already exists")

    db.add(permission)
    await db.commit()
    await db.refresh(permission)
    return permission


@router.get("/permissions", response_model=list[Permission])
async def list_permissions(db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(Permission))
    return result.scalars().all()


@router.delete("/permissions/{permission_id}")
async def delete_permission(
    permission_id: UUID, db: AsyncSession = Depends(get_async_session)
):
    permission = await db.get(Permission, permission_id)
    if not permission:
        raise AppException(404, ErrorCode.NOT_FOUND, "Permission not found")

    await db.delete(permission)
    await db.commit()
    return {"message": "Permission deleted"}


@router.post("/{role_id}/permissions/{permission_id}")
async def assign_permission_to_role(
    role_id: UUID,
    permission_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    role = await db.get(Role, role_id)
    permission = await db.get(Permission, permission_id)

    if not role or not permission:
        raise AppException(404, ErrorCode.NOT_FOUND, "Role or Permission not found")

    existing = await db.execute(
        select(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id,
        )
    )
    if existing.scalar_one_or_none():
        raise AppException(400, ErrorCode.BAD_REQUEST, "Permission already assigned")

    rp = RolePermission(role_id=role_id, permission_id=permission_id)
    db.add(rp)
    await db.commit()
    return {"message": "Permission assigned to role"}


@router.delete("/{role_id}/permissions/{permission_id}")
async def remove_permission_from_role(
    role_id: UUID,
    permission_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    result = await db.execute(
        select(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id,
        )
    )
    rp = result.scalar_one_or_none()
    if not rp:
        raise AppException(404, ErrorCode.NOT_FOUND, "Permission not assigned")

    await db.delete(rp)
    await db.commit()
    return {"message": "Permission removed from role"}
