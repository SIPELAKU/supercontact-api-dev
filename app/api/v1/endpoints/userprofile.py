from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import auth_require
from app.db.session import get_async_session
from app.repositories.userprofile_repository import UserProfileRepository
from app.schemas import ResponseModel
from app.schemas.userprofile_schema import UserProfileResponse, AboutSchema
from app.services.userprofile_service import UserProfileService

router = APIRouter(prefix="/user-profile", tags=["User Profile"])

repo = UserProfileRepository()
service = UserProfileService(repo)


@router.get("/about", response_model=ResponseModel[UserProfileResponse])
async def get_current_user_profile(db: AsyncSession = Depends(get_async_session), current_user=Depends(auth_require)):
    profile = await service.get_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return ResponseModel(data=profile)


@router.patch("/about", response_model=ResponseModel[AboutSchema])
async def update_about(payload: AboutSchema, db: AsyncSession = Depends(get_async_session),
                       current_user=Depends(auth_require)):
    detail = await service.update_about(db, current_user.id, payload.model_dump(exclude_unset=True))
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return ResponseModel(data=detail)
