from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.role_model import Role
from app.exceptions import AppException
from app.schemas.error_schema import ErrorCode


class RoleService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_role(
        self,
        role_name: str,
        is_system_role: bool = False,
    ) -> Role:

        existing = await self.db.execute(
            select(Role).where(Role.role_name == role_name)
        )
        if existing.scalar():
            raise AppException(
                ErrorCode.BAD_REQUEST,
                "Role name already exists",
            )

        role = Role(
            role_name=role_name,
            is_system_role=is_system_role,
        )

        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def get_roles(self) -> List[Role]:
        result = await self.db.execute(select(Role))
        return result.scalars().all()

    async def get_role_by_id(self, role_id: UUID) -> Role:
        result = await self.db.execute(select(Role).where(Role.id == role_id))
        role = result.scalar()

        if not role:
            raise AppException(
                ErrorCode.ROLE_NOT_FOUND,
                "Role not found",
            )

        return role

    async def update_role(
        self,
        role_id: UUID,
        role_name: Optional[str] = None,
        is_system_role: Optional[bool] = None,
    ) -> Role:

        role = await self.get_role_by_id(role_id)

        if role_name and role_name != role.role_name:
            existing = await self.db.execute(
                select(Role).where(Role.role_name == role_name)
            )
            if existing.scalar():
                raise AppException(
                    ErrorCode.BAD_REQUEST,
                    "Role name already exists",
                )
            role.role_name = role_name

        if is_system_role is not None:
            role.is_system_role = is_system_role

        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def delete_role(self, role_id: UUID) -> None:
        role = await self.get_role_by_id(role_id)
        await self.db.delete(role)
        await self.db.commit()
