from datetime import datetime, timezone
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import or_, func, delete
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import UserOTP, User, UserOTPType
from app.schemas import UserGetQuery


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_users(self, query_params: UserGetQuery):
        query = select(User).options(
            selectinload(User.manage_user),
            selectinload(User.detail),
        )

        if query_params.search:
            query = query.where(
                or_(
                    User.fullname.ilike(f"%{query_params.search}%"),
                    User.email.ilike(f"%{query_params.search}%"),
                )
            )

        if query_params.position:
            query = query.where(User.position == query_params.position)

        # Pagination
        skip = (query_params.page - 1) * query_params.limit
        query = query.offset(skip).limit(query_params.limit)
        result = await self.db.scalars(query)
        users = result.all()

        # Count total rows
        total_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(total_query)

        return users, total

    async def get_by_email(self, email: EmailStr):
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.manage_user))
            .where(User.email == email)
        )
        return result.scalars().first()

    async def get_by_id(self, user_id: UUID):
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.manage_user))
            .where(User.id == user_id)
        )
        return result.scalars().first()

    # CREATE
    async def create(self, user: User):
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    # UPDATE
    async def update(self, user: User):
        await self.db.commit()
        await self.db.refresh(user)
        return user

    # DELETE
    async def delete(self, user: User):
        await self.db.delete(user)
        await self.db.commit()

    async def get_all(self):
        result = await self.db.execute(select(User))
        return result.scalars().all()

    async def get_total(self):
        return await self.db.scalar(select(func.count()).select_from(User))

    async def count_user_otp_active(self, user_id: UUID):
        query = select(func.count(UserOTP.id)).where(
            UserOTP.user_id == user_id,
            UserOTP.expires_at > datetime.now(timezone.utc),
        )
        result = await self.db.exec(query)
        return result.one()

    async def create_user_otp(self, user_otp: UserOTP):
        self.db.add(user_otp)
        await self.db.commit()
        return user_otp

    async def get_active_user_otp(self, user_id: UUID, otp_type: UserOTPType) -> UserOTP:
        query = (
            select(UserOTP)
            .where(UserOTP.user_id == user_id)
            .where(UserOTP.otp_type == otp_type)
            .order_by(UserOTP.created_at.desc())
        )

        return (await self.db.exec(query)).first()

    async def delete_all_user_otp(self, user_id: UUID, otp_type: UserOTPType):
        query = (
            delete(UserOTP)
            .where(UserOTP.user_id == user_id)
            .where(UserOTP.otp_type == otp_type)
        )

        await self.db.exec(query)
        await self.db.commit()
