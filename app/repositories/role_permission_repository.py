from typing import List
from uuid import UUID
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.role_model import Role, Permission, RolePermission
from app.schemas.role_permission_schema import RoleGetQuery


class RolePermissionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_role(self, role: Role, permissions: List[str]):

        self.db.add(role)
        await self.db.flush()

        for perm_name in permissions:

            perm_stmt = select(Permission).where(Permission.name == perm_name)
            existing_perm = await self.db.scalar(perm_stmt)

            if not existing_perm:
                new_perm = Permission(name=perm_name)
                self.db.add(new_perm)
                await self.db.flush()
                perm_id = new_perm.id
            else:
                perm_id = existing_perm.id

            pivot = RolePermission(role_id=role.id, permission_id=perm_id)
            self.db.add(pivot)

        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def get_roles(self, query_params: RoleGetQuery):
        query = select(Role)

        query = query.options(selectinload(Role.permissions))

        if query_params.search:
            query = query.where(Role.name.ilike(f"%{query_params.search}%"))

        if query_params.permission:
            query = (
                query.join(RolePermission)
                .join(Permission)
                .where(Permission.name.in_(query_params.permission))
            )

        sort_col = getattr(Role, query_params.sort_by)
        if query_params.sort_order == "desc":
            sort_col = sort_col.desc()
        else:
            sort_col = sort_col.asc()

        query = query.order_by(sort_col)

        count_stmt = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_stmt)

        offset = (query_params.page - 1) * query_params.limit
        result = await self.db.exec(query.offset(offset).limit(query_params.limit))
        roles = result.unique().all()

        return roles, total

    async def get_role_by_id(self, role_id):
        stmt = (
            select(Role)
            .where(Role.id == role_id)
            .options(selectinload(Role.permissions))
        )
        return await self.db.scalar(stmt)

    async def get_role_by_name(self, name: str):
        stmt = select(Role).where(Role.name == name)
        return await self.db.scalar(stmt)

    async def update_role(self, role: Role, payload):

        if payload.name:
            role.name = payload.name

        if payload.permissions is not None:
            await self._sync_role_permissions(role.id, payload.permissions)

        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def _sync_role_permissions(self, role_id: UUID, permissions: List[str]):
        delete_stmt = select(RolePermission).where(RolePermission.role_id == role_id)
        existing = (await self.db.exec(delete_stmt)).all()

        for row in existing:
            await self.db.delete(row)

        await self.db.flush()

        for perm_name in permissions:
            stmt = select(Permission).where(Permission.name == perm_name)
            perm = await self.db.scalar(stmt)

            if not perm:
                perm = Permission(name=perm_name)
                self.db.add(perm)
                await self.db.flush()

            pivot = RolePermission(role_id=role_id, permission_id=perm.id)
            self.db.add(pivot)

        await self.db.flush()

    async def delete_role(self, role: Role):

        stmt = select(RolePermission).where(RolePermission.role_id == role.id)
        pivots = (await self.db.exec(stmt)).all()
        for p in pivots:
            await self.db.delete(p)

        await self.db.delete(role)
        await self.db.commit()
