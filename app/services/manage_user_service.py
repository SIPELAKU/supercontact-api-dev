from typing import List, Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.user_model import User
from app.models.role_model import Role
from app.models.department_model import Department
from app.models.branch_model import Branch
from app.schemas.user_schema import (
    UserCreateRequest,
    UserUpdateRequest,
)
from app.exceptions import AppException
from app.schemas.error_schema import ErrorCode
from app.repository.user_repository import UserRepository
from app.repository.auth_repository import AuthRepository


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)
        self.auth_repo = AuthRepository(db)

    async def _get_role_by_name(self, role_name: str) -> Role:
        result = await self.db.execute(select(Role).where(Role.role_name == role_name))
        role = result.scalars().first()
        if not role:
            raise AppException(ErrorCode.ROLE_NOT_FOUND, "Role not found")
        return role

    async def _get_department_by_name(
        self, department_name: Optional[str]
    ) -> Optional[Department]:
        if not department_name:
            return None

        result = await self.db.execute(
            select(Department).where(Department.name == department_name)
        )
        department = result.scalars().first()
        if not department:
            raise AppException(ErrorCode.DEPARTMENT_NOT_FOUND, "Department not found")
        return department

    async def _get_branch_by_name(self, branch_name: Optional[str]) -> Optional[Branch]:
        if not branch_name:
            return None

        result = await self.db.execute(select(Branch).where(Branch.name == branch_name))
        branch = result.scalars().first()
        if not branch:
            raise AppException(ErrorCode.BRANCH_NOT_FOUND, "Branch not found")
        return branch

    async def _validate_branch_belongs_to_department(
        self,
        branch: Optional[Branch],
        department: Optional[Department],
    ):
        if not branch or not department:
            return

        if branch.department_id != department.id:
            raise AppException(
                ErrorCode.BRANCH_NOT_IN_DEPARTMENT,
                "Branch does not belong to selected department",
            )

    async def _check_unique_employee_id(
        self,
        employee_id: Optional[str],
        exclude_user_id: Optional[UUID] = None,
    ):
        if not employee_id:
            return

        query = select(User).where(User.employee_id == employee_id)
        if exclude_user_id:
            query = query.where(User.id != exclude_user_id)

        result = await self.db.execute(query)
        if result.scalars().first():
            raise AppException(
                ErrorCode.USER_EMPLOYEE_ID_EXISTS,
                "Employee ID already used",
            )

    async def create_user(self, data: UserCreateRequest) -> User:
        """ """
        auth_user = await self.auth_repo.get_by_email(data.email)
        if not auth_user:
            raise AppException(
                ErrorCode.USER_NOT_REGISTERED,
                "Email belum terdaftar",
            )

        user_id = auth_user.user_id

        exists = await self.repo.get_by_user_id(user_id)
        if exists:
            raise AppException(
                ErrorCode.USER_ALREADY_EXISTS,
                "User sudah ditambahkan",
            )

        role = await self._get_role_by_name(data.role)
        department = await self._get_department_by_name(data.department)
        branch = await self._get_branch_by_name(data.branch)

        await self._validate_branch_belongs_to_department(branch, department)

        user = User(
            user_id=user_id,
            role_id=role.id,
            department_id=department.id if department else None,
            branch_id=branch.id if branch else None,
            user_level=data.user_level,
            employee_id=data.employee_id,
            status=data.status,
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    # GET USER
    async def get_user(self, user_id: UUID) -> User:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise AppException(ErrorCode.USER_NOT_FOUND, "User not found")
        return user

    # LIST USERS

    async def list_users(self, skip: int = 0, limit: int = 20) -> List[User]:
        result = await self.db.execute(
            select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    # UPDATE USER

    async def update_user(self, user_id: UUID, data: UserUpdateRequest) -> User:
        user = await self.get_user(user_id)

        if data.role:
            role = await self._get_role_by_name(data.role)
            user.role_id = role.id

        if data.department is not None:
            department = await self._get_department_by_name(data.department)
            user.department_id = department.id if department else None

        if data.branch is not None:
            branch = await self._get_branch_by_name(data.branch)
            user.branch_id = branch.id if branch else None

        if data.user_level is not None:
            user.user_level = data.user_level

        if data.employee_id is not None:
            await self._check_unique_employee_id(data.employee_id, user.id)
            user.employee_id = data.employee_id

        if data.status is not None:
            user.status = data.status

        await self.db.commit()
        await self.db.refresh(user)
        return user

    # DELETE USER
    async def delete_user(self, user_id: UUID):
        user = await self.get_user(user_id)
        await self.db.delete(user)
        await self.db.commit()
