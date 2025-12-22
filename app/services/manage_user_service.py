import random
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.exceptions import AppException
from app.models.manage_user_model import (
    ManageUser,
    UserLevel,
    Position,
    UserStatus,
)
from app.models.user_model import User
from app.models.role_model import Role
from app.models.branch_model import Branch
from app.models.department_enum import DepartmentEnum
from app.repositories.manage_user_repository import ManageUserRepository
from app.schemas.manage_user_schema import (
    ManageUserCreateRequest,
    ManageUserUpdateRequest,
    ManageUserResponse,
    ManageUserListResponse,
)
from app.schemas.error_schema import ErrorCode


class ManageUserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ManageUserRepository(db)

    async def _get_or_404(self, model, condition, code: ErrorCode):
        result = await self.db.execute(select(model).where(condition))
        obj = result.scalars().first()
        if not obj:
            raise AppException(
                status_code=404,
                code=code,
                message="Data not found",
            )
        return obj

    def _validate_position(
        self,
        user_level: UserLevel,
        position: Optional[Position],
    ):
        if user_level in {UserLevel.MANAGER, UserLevel.SUPERVISOR} and not position:
            raise AppException(
                status_code=400,
                code=ErrorCode.BAD_REQUEST,
                message="Position is required for manager or supervisor",
            )

    def _validate_status_transition(
        self,
        current: UserStatus,
        new: UserStatus,
    ):
        if current == new:
            return

        allowed = {
            UserStatus.PENDING: {UserStatus.ACTIVE},
            UserStatus.ACTIVE: {UserStatus.INACTIVE},
            UserStatus.INACTIVE: {UserStatus.ACTIVE},
        }

        if new not in allowed.get(current, set()):
            raise AppException(
                status_code=400,
                code=ErrorCode.INVALID_STATUS_TRANSITION,
                message=f"Cannot change status from {current} to {new}",
            )

    async def _generate_employee_id(self, department: DepartmentEnum) -> str:
        while True:
            emp_id = f"{department.code}-{random.randint(100, 999)}"
            if not await self.repo.get_by_employee_id(emp_id):
                return emp_id

    async def _validate_single_manager_per_branch(
        self,
        *,
        branch_id: UUID,
        current_manage_user_id: Optional[UUID] = None,
    ):
        exists = await self.repo.manager_exists_in_branch(
            branch_id=branch_id,
            exclude_user_id=current_manage_user_id,
        )
        if exists:
            raise AppException(
                status_code=409,
                code=ErrorCode.MANAGER_ALREADY_EXISTS,
                message="Manager already exists in this branch",
            )

    def _to_response(self, mu: ManageUser) -> ManageUserResponse:
        return ManageUserResponse(
            id=mu.id,
            user_id=mu.user.id,
            fullname=mu.user.fullname,
            email=mu.user.email,
            avatar_initial=mu.user.avatar_initial,
            role=mu.role.role_name if mu.role else None,
            department=mu.branch.department.value if mu.branch else None,
            branch=mu.branch.name if mu.branch else None,
            user_level=mu.user_level,
            position=mu.position,
            employee_id=mu.employee_id,
            status=mu.status,
            created_at=mu.created_at,
            updated_at=mu.updated_at,
        )

    # CREATE
    async def create(self, data: ManageUserCreateRequest) -> ManageUserResponse:
        user = await self._get_or_404(
            User,
            User.email == data.email,
            ErrorCode.USER_NOT_FOUND,
        )

        if await self.repo.get_by_user_id(user.id):
            raise AppException(
                status_code=409,
                code=ErrorCode.USER_ALREADY_ASSIGNED,
                message="User already assigned",
            )

        branch: Optional[Branch] = None
        role_id: Optional[UUID] = None
        employee_id: Optional[str] = None

        if data.department and data.branch:
            department = DepartmentEnum(data.department)
            branch = await self._get_or_404(
                Branch,
                (Branch.name == data.branch) & (Branch.department == department),
                ErrorCode.BRANCH_NOT_FOUND,
            )
            employee_id = await self._generate_employee_id(branch.department)

        if data.role:
            role = await self._get_or_404(
                Role,
                Role.role_name == data.role,
                ErrorCode.ROLE_NOT_FOUND,
            )
            role_id = role.id

        user_level = data.user_level or UserLevel.STAFF
        self._validate_position(user_level, data.position)

        if user_level == UserLevel.MANAGER:
            if not branch:
                raise AppException(
                    status_code=400,
                    code=ErrorCode.BRANCH_REQUIRED_FOR_MANAGER,
                    message="Branch is required for manager",
                )
            await self._validate_single_manager_per_branch(branch_id=branch.id)

        mu = ManageUser(
            user_id=user.id,
            role_id=role_id,
            branch_id=branch.id if branch else None,
            employee_id=employee_id,
            user_level=user_level,
            position=data.position,
            status=UserStatus.PENDING,
        )

        await self.repo.create(mu)
        return await self.get_by_id(mu.id)

    # GET BY ID
    async def get_by_id(self, id: UUID) -> ManageUserResponse:
        result = await self.db.execute(
            select(ManageUser)
            .where(ManageUser.id == id)
            .options(
                selectinload(ManageUser.user),
                selectinload(ManageUser.role),
                selectinload(ManageUser.branch),
            )
        )
        mu = result.scalars().first()
        if not mu:
            raise AppException(
                status_code=404,
                code=ErrorCode.MANAGE_USER_NOT_FOUND,
                message="Manage user not found",
            )
        return self._to_response(mu)

    # UPDATE
    async def update(
        self,
        id: UUID,
        data: ManageUserUpdateRequest,
    ) -> ManageUserResponse:

        mu = await self._get_or_404(
            ManageUser,
            ManageUser.id == id,
            ErrorCode.MANAGE_USER_NOT_FOUND,
        )

        if data.department is not None and data.branch is not None:
            department = DepartmentEnum(data.department)
            branch = await self._get_or_404(
                Branch,
                (Branch.name == data.branch) & (Branch.department == department),
                ErrorCode.BRANCH_NOT_FOUND,
            )

            mu.branch_id = branch.id

            if mu.user_level == UserLevel.MANAGER:
                await self._validate_single_manager_per_branch(
                    branch_id=branch.id,
                    current_manage_user_id=mu.id,
                )

            if not mu.employee_id:
                mu.employee_id = await self._generate_employee_id(branch.department)

        if data.role is not None:
            role = await self._get_or_404(
                Role,
                Role.role_name == data.role,
                ErrorCode.ROLE_NOT_FOUND,
            )
            mu.role_id = role.id

        if data.user_level is not None:
            self._validate_position(data.user_level, data.position)

            if data.user_level == UserLevel.MANAGER:
                if not mu.branch_id:
                    raise AppException(
                        status_code=400,
                        code=ErrorCode.BRANCH_REQUIRED_FOR_MANAGER,
                        message="Branch is required for manager",
                    )

                await self._validate_single_manager_per_branch(
                    branch_id=mu.branch_id,
                    current_manage_user_id=mu.id,
                )

            mu.user_level = data.user_level

        if data.position is not None:
            mu.position = data.position

        if data.status is not None:
            self._validate_status_transition(mu.status, data.status)
            mu.status = data.status

        await self.repo.update(mu)
        return await self.get_by_id(mu.id)

    # DEACTIVATE
    async def deactivate(self, id: UUID):
        mu = await self._get_or_404(
            ManageUser,
            ManageUser.id == id,
            ErrorCode.MANAGE_USER_NOT_FOUND,
        )

        self._validate_status_transition(mu.status, UserStatus.INACTIVE)
        mu.status = UserStatus.INACTIVE
        await self.repo.update(mu)

    # LIST
    async def list(
        self,
        *,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        status: Optional[UserStatus] = None,
        role_id: Optional[UUID] = None,
    ) -> ManageUserListResponse:

        total, items = await self.repo.list(
            page=page,
            limit=limit,
            search=search,
            status=status,
            role_id=role_id,
        )

        return ManageUserListResponse(
            total=total,
            items=[self._to_response(mu) for mu in items],
        )

    # HARD DELETE
    async def hard_delete(self, id: UUID):
        mu = await self._get_or_404(
            ManageUser,
            ManageUser.id == id,
            ErrorCode.MANAGE_USER_NOT_FOUND,
        )
        await self.repo.hard_delete(mu)
