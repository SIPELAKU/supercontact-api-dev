from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import auth_require
from app.db.session import get_async_session
from app.schemas import ChangePasswordSchema, UserDeviceResponse, ResponseModel
from app.services.userdevice_service import UserSecurityService

router = APIRouter(prefix="/profile-security", tags=["User Profile"])

security_service = UserSecurityService()


@router.patch("/profile/security/password")
async def change_password(
        payload: ChangePasswordSchema,
        db: AsyncSession = Depends(get_async_session),
        current_user=Depends(auth_require),
):
    await security_service.change_password(
        db, current_user.id, payload
    )
    return ResponseModel(success=True)


# @router.post("/profile/security/2fa")
# async def enable_2fa(
#     db: AsyncSession = Depends(get_async_session),
#     current_user=Depends(auth_require),
# ):
#     enabled = await security_service.enable_2fa(db, current_user)
#     return ResponseModel(
#         data={"two_factor_enabled": enabled}
#     )


@router.get(
    "/profile/security/devices",
    response_model=ResponseModel[list[UserDeviceResponse]]
)
async def get_recent_devices(
        db: AsyncSession = Depends(get_async_session),
        current_user=Depends(auth_require),
):
    devices = await security_service.get_recent_devices(
        db, current_user.id
    )
    return ResponseModel(data=devices)
