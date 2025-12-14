from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.schemas.userprofile_schema import UserProfileResponse, AboutSchema
from app.repositories.userprofile_repository import UserProfileRepository
from app.services.userprofile_service import UserProfileService
from app.db.session import get_async_session
from app.core.security import auth_require
from typing import List
from app.schemas import ResponseModel


router = APIRouter(prefix="/user-profile", tags=["User Profile"])

repo = UserProfileRepository()
service = UserProfileService(repo)

@router.get("/profile", response_model=ResponseModel[UserProfileResponse])
async def get_current_user_profile(db: AsyncSession = Depends(get_async_session), current_user=Depends(auth_require)):
    profile = await service.get_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return ResponseModel(data=profile)

@router.put("/profile/about", response_model=ResponseModel[AboutSchema])
async def update_about(payload: AboutSchema, db: AsyncSession = Depends(get_async_session), current_user=Depends(auth_require)):
    detail = await service.update_about(db, current_user.id, payload.dict(exclude_unset=True))
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return ResponseModel(data=detail)