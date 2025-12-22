from typing import Optional, List
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.exceptions import AppException
from app.models.manage_user_model import UserLevel
from app.models.department_enum import DepartmentEnum
from app.repositories.manage_user_repository import ManageUserRepository
from app.repositories.department_repository import DepartmentRepository
from app.schemas.error_schema import ErrorCode
from app.services.manage_user_service import ManageUserService


class DepartmentDetailService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.manage_user_repo = ManageUserRepository(db)
        self.department_repo = DepartmentRepository(db)
        self.manage_user_service = ManageUserService(db)

    async def get_detail(
        self,
        *,
        department: DepartmentEnum,
        branch_id: Optional[UUID] = None,
    ):

        branch = None
        if branch_id:
            branch = await self.department_repo.get_department_branch_by_id(
                department=department,
                branch_id=branch_id,
            )

        users = await self.manage_user_repo.get_active_users_by_department(
            department=department,
            branch_id=branch_id,
            user_levels=[UserLevel.STAFF],
        )

        items = [self.manage_user_service._to_response(mu) for mu in users]

        return {
            "department": department.value,
            "department_code": department.code,
            "branch": branch.name if branch else None,
            "branch_id": branch.id if branch else None,
            "total_staff": len(items),
            "staff": items,
        }
