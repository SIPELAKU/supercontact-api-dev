from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import auth_require
from app.db.session import get_async_session
from app.models import User
from app.schemas import (
    MailingCreate, MailingUpdate,
    PaginatedMailings, MailingResponse,
    ResponseModel, MailingDeleteResponse
)
from app.services.mailing_service import MailingService

router = APIRouter(prefix="/mailings", tags=["Mailings"])


async def get_mailing_service(db: AsyncSession = Depends(get_async_session)):
    return MailingService(db=db)


@router.get("/", response_model=ResponseModel[PaginatedMailings], dependencies=[Depends(auth_require)])
async def get_all_mailings(
        page: int = 1,
        limit: int = 10,
        search: str = None,
        service: MailingService = Depends(get_mailing_service),
        current_user=Depends(auth_require)
):
    query = type("Query", (), {
        "page": page,
        "limit": limit,
        "search": search,
    })
    result = await service.find_all_mailings(user_id=current_user.id, query=query)
    mailings = [MailingResponse.model_validate(c) for c in result["data"]]

    return ResponseModel(data=PaginatedMailings(
        total=result["total"],
        page=result["page"],
        limit=result["limit"],
        total_pages=result["total_pages"],
        mailings=mailings
    ))


@router.post("/", response_model=ResponseModel[MailingResponse],
             dependencies=[Depends(auth_require)])
async def create_mailing(
        data: MailingCreate,
        service: MailingService = Depends(get_mailing_service),
        current_user=Depends(auth_require)
):
    mailing = await service.create_mailing(user_id=current_user.id, data=data)

    return ResponseModel(
        data=mailing
    )


@router.get("/{mailing_id}", response_model=ResponseModel[MailingResponse], dependencies=[Depends(auth_require)])
async def get_mailing_by_id(mailing_id: UUID, service: MailingService = Depends(get_mailing_service),
                            current_user: User = Depends(auth_require)):
    mailing = await service.find_one_mailing(user_id=current_user.id, mailing_id=mailing_id)

    return ResponseModel(data=mailing)


@router.put("/{mailing_id}", response_model=ResponseModel[MailingResponse])
async def update_contact_by_id(mailing_id: UUID, data: MailingUpdate,
                               service: MailingService = Depends(get_mailing_service),
                               current_user: User = Depends(auth_require)):
    updated = await service.update_mailing(user_id=current_user.id, mailing_id=mailing_id, data=data)

    return ResponseModel(data=updated)


@router.delete("/{mailing_id}", response_model=ResponseModel[MailingDeleteResponse])
async def delete_mailing_by_id(mailing_id: UUID, service: MailingService = Depends(get_mailing_service),
                               current_user: User = Depends(auth_require)):
    mailing = await service.delete_mailing(user_id=current_user.id, mailing_id=mailing_id)

    return ResponseModel(data={"id": mailing_id, "deleted": mailing})
