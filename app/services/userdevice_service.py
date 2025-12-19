from app.core.security import verify_password, hash_password
from fastapi import HTTPException
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_model import User
from sqlalchemy import select
from app.models.userdevice_model import UserDevice
from app.schemas.userdevice_schema import ChangePasswordSchema

class UserSecurityService:
    async def change_password(
        self,
        db: AsyncSession,
        user_id: UUID,
        payload: ChangePasswordSchema,
    ):
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(payload.current_password, user.password):
            raise HTTPException(
                status_code=400,
                detail="Current password is incorrect"
            )

        if payload.new_password != payload.confirm_password:
            raise HTTPException(
                status_code=400,
                detail="Password confirmation does not match"
            )

        user.password = hash_password(payload.new_password)

        await db.commit()
        await db.refresh(user)

    # async def enable_2fa(
    #         self,
    #         db: AsyncSession,
    #         user: User,
    # ):
    #     user.two_factor_enabled = True
    #     await db.commit()
    #     return user.two_factor_enabled


    async def get_recent_devices(
        self,
        db: AsyncSession,
        user_id: UUID,
    ):
        result = await db.execute(
            select(UserDevice)
                .where(UserDevice.user_id == user_id)
                .order_by(UserDevice.last_activity.desc())
                .limit(10)
        )
        return result.scalars().all()
