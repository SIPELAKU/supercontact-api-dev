from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_async_session
from app.schemas import (
    LeadRequest,
    LeadResponse,
    LeadListResponse,
    ResponseModel,
    LeadGetQuery,
    LeadUpdateStatus
)
from app.services import LeadService

router = APIRouter(prefix="/leads", tags=["Leads"])


def get_lead_service(db: AsyncSession = Depends(get_async_session)):
    return LeadService(db)


# CREATE NEW LEAD
@router.post(
    "",
    response_model=ResponseModel[LeadResponse],
    # dependencies=[Depends(auth_require)]
)
async def create_lead(payload: LeadRequest, service: LeadService = Depends(get_lead_service)):
    data = await service.create_lead(payload)
    return ResponseModel(data=data)


# GET ALL LEADS
@router.get(
    "",
    response_model=ResponseModel[LeadListResponse],
    # dependencies=[Depends(auth_require)]
)
async def get_all_leads(
        query_params: LeadGetQuery = Depends(LeadGetQuery),
        service: LeadService = Depends(get_lead_service)
):
    data = await service.find_all_leads(query_params=query_params)
    return ResponseModel(data=LeadListResponse(**data))


# GET LEAD BY ID
@router.get(
    "/{lead_id}",
    response_model=ResponseModel[LeadResponse],
    # dependencies=[Depends(auth_require)]
)
async def get_lead_by_id(lead_id: UUID, service: LeadService = Depends(get_lead_service)):
    data = await service.find_one_lead(lead_id)
    return ResponseModel(data=data)


# UPDATE LEAD
@router.put(
    "/{lead_id}",
    response_model=ResponseModel[LeadResponse],
    # dependencies=[Depends(auth_require)]
)
async def update_lead_by_id(lead_id: UUID, payload: LeadRequest, service: LeadService = Depends(get_lead_service)):
    data = await service.update_lead(lead_id, payload)
    return ResponseModel(data=data)


# UPDATE LEAD STATUS
@router.patch(
    "/{lead_id}/status",
    response_model=ResponseModel[LeadResponse],
    # dependencies=[Depends(auth_require)]
)
async def update_lead_status_by_id(
        lead_id: UUID,
        payload: LeadUpdateStatus,
        service: LeadService = Depends(get_lead_service)
):
    data = await service.update_lead_status(lead_id, payload)
    return ResponseModel(data=data)
