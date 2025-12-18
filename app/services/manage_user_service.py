from typing import Optional
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.exceptions import AppException
from app.models.manage_user_model import ManageUser
from app.models.role_model import Role
from app.models.department_model import Department
from app.models.branch_model import Branch
from app.models.user_model import User
from app.schemas.manage_user_schema import (
    ManageUserCreateRequest,
    ManageUserUpdateRequest,
    ManageUserResponse,
    UserLevel,
)
from app.schemas.error_schema import ErrorCode


class ManageUserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_or_404(self, model, condition, code, message):
        result = await self.db.execute(select(model).where(condition))
        obj = result.scalars().first()
        if not obj:
            raise AppException(status_code=404, code=code, message=message)
        return obj

    async def _validate_unique_employee_id(
        self, employee_id: Optional[str], exclude_id: Optional[UUID] = None
    ):
        if not employee_id:
            return

        query = select(ManageUser).where(ManageUser.employee_id == employee_id)
        if exclude_id:
            query = query.where(ManageUser.id != exclude_id)

        result = await self.db.execute(query)
        if result.scalars().first():
            raise AppException(
                status_code=409,
                code=ErrorCode.EMPLOYEE_ID_ALREADY_EXISTS,
                message="Employee ID already exists",
            )

    def _validate_position_rule(self, user_level: UserLevel, position):
        if user_level in {UserLevel.SUPERVISOR, UserLevel.MANAGER} and not position:
            raise AppException(
                status_code=400,
                code=ErrorCode.INVALID_POSITION,
                message="Supervisor or Manager must have a position",
            )

    async def _to_response(self, mu: ManageUser) -> ManageUserResponse:
        user = await self.db.get(User, mu.user_id)

        role_name = None
        department_name = None
        branch_name = None

        if mu.role_id:
            role = await self.db.get(Role, mu.role_id)
            role_name = role.role_name if role else None

        if mu.department_id:
            department = await self.db.get(Department, mu.department_id)
            department_name = department.name if department else None

        if mu.branch_id:
            branch = await self.db.get(Branch, mu.branch_id)
            branch_name = branch.name if branch else None

        return ManageUserResponse(
            id=mu.id,
            user_id=user.id,
            fullname=user.fullname,
            email=user.email,
            role=role_name,
            department=department_name,
            branch=branch_name,
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
            "User not found",
        )

        exists = await self.db.execute(
            select(ManageUser).where(ManageUser.user_id == user.id)
        )
        if exists.scalars().first():
            raise AppException(
                status_code=409,
                code=ErrorCode.USER_ALREADY_ASSIGNED,
                message="User already activated",
            )

        role_id = None
        department_id = None
        branch_id = None

        if data.role:
            role = await self._get_or_404(
                Role,
                Role.role_name == data.role,
                ErrorCode.ROLE_NOT_FOUND,
                "Role not found",
            )
            role_id = role.id

        if data.department:
            department = await self._get_or_404(
                Department,
                Department.name == data.department,
                ErrorCode.DEPARTMENT_NOT_FOUND,
                "Department not found",
            )
            department_id = department.id

            if data.branch:
                branch = await self._get_or_404(
                    Branch,
                    (Branch.name == data.branch)
                    & (Branch.department_id == department.id),
                    ErrorCode.BRANCH_NOT_FOUND,
                    "Branch not found in selected department",
                )
                branch_id = branch.id

        await self._validate_unique_employee_id(data.employee_id)
        self._validate_position_rule(data.user_level, data.position)

        mu = ManageUser(
            user_id=user.id,
            role_id=role_id,
            department_id=department_id,
            branch_id=branch_id,
            user_level=data.user_level,
            position=data.position,
            employee_id=data.employee_id,
            status=data.status,
        )

        self.db.add(mu)
        await self.db.commit()
        await self.db.refresh(mu)

        return await self._to_response(mu)

    # UPDATE
    async def update(
        self, id: UUID, data: ManageUserUpdateRequest
    ) -> ManageUserResponse:
        mu = await self._get_or_404(
            ManageUser,
            ManageUser.id == id,
            ErrorCode.MANAGE_USER_NOT_FOUND,
            "Manage user not found",
        )

        payload = data.model_dump(exclude_unset=True)

        if "role" in payload and not payload["role"]:
            raise AppException(400, ErrorCode.INVALID_REQUEST, "Role is required")

        if "department" in payload and not payload["department"]:
            raise AppException(400, ErrorCode.INVALID_REQUEST, "Department is required")

        if "role" in payload:
            role = await self._get_or_404(
                Role,
                Role.role_name == payload["role"],
                ErrorCode.ROLE_NOT_FOUND,
                "Role not found",
            )
            mu.role_id = role.id

        if "department" in payload:
            department = await self._get_or_404(
                Department,
                Department.name == payload["department"],
                ErrorCode.DEPARTMENT_NOT_FOUND,
                "Department not found",
            )
            mu.department_id = department.id
            mu.branch_id = None

        if "branch" in payload:
            if payload["branch"]:
                branch = await self._get_or_404(
                    Branch,
                    (Branch.name == payload["branch"])
                    & (Branch.department_id == mu.department_id),
                    ErrorCode.BRANCH_NOT_FOUND,
                    "Branch not found",
                )
                mu.branch_id = branch.id
            else:
                mu.branch_id = None

        if "employee_id" in payload:
            await self._validate_unique_employee_id(
                payload["employee_id"], exclude_id=id
            )

        new_level = payload.get("user_level", mu.user_level)
        new_position = payload.get("position", mu.position)
        self._validate_position_rule(new_level, new_position)

        for field in ["user_level", "position", "employee_id", "status"]:
            if field in payload:
                setattr(mu, field, payload[field])

        await self.db.commit()
        await self.db.refresh(mu)
        return await self._to_response(mu)
