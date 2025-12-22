from typing import Optional, List
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.manage_user_model import UserLevel, UserStatus
from app.models.department_enum import DepartmentEnum
from app.repositories.manage_user_repository import ManageUserRepository
from app.repositories.department_repository import DepartmentRepository
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
        search: Optional[str] = None,
        status: Optional[UserStatus] = None,
    ):
        """
        Department detail with:
        - filter branch
        - search user
        - filter user status
        """

        branch = None
        if branch_id:
            branch = await self.department_repo.get_department_branch_by_id(
                department=department,
                branch_id=branch_id,
            )

        users = await self.manage_user_repo.get_users_by_department_detail(
            department=department,
            branch_id=branch_id,
            search=search,
            status=status,
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
