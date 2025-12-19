from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.role_model import Role
from app.exceptions import AppException
from app.schemas.error_schema import ErrorCode


class RoleService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # CREATE
    async def create(self, role_name: str) -> Role:
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
            is_system_role=False,
        )

        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        return role

    # LIST
    async def get_all(self) -> List[Role]:
        result = await self.db.execute(select(Role))
        return result.scalars().all()

    async def get_by_id(self, role_id: UUID) -> Role:
        result = await self.db.execute(select(Role).where(Role.id == role_id))
        role = result.scalar_one_or_none()

        if not role:
            raise AppException(
                ErrorCode.ROLE_NOT_FOUND,
                "Role not found",
            )

        return role
