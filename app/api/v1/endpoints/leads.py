from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import auth_require
from app.db import get_async_session
from app.models import LeadStatus, LeadSource
from app.schemas import (
    LeadRequest,
    LeadResponse,
    LeadSortBy,
    SortOrder,
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
    dependencies=[Depends(auth_require)]
)
async def create_lead(payload: LeadRequest, service: LeadService = Depends(get_lead_service)):
    data = await service.create_lead(payload)
    return ResponseModel(data=data)


# GET ALL LEADS
@router.get(
    "",
    response_model=ResponseModel[LeadListResponse],
    dependencies=[Depends(auth_require)]
)
async def get_all_leads(
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        status: Optional[List[LeadStatus]] = Query(None),
        source: Optional[List[LeadSource]] = Query(None),
        assigned_to: Optional[List[UUID]] = Query(None),
        date_from: Optional[date] = Query(None),
        date_to: Optional[date] = Query(None),
        search: Optional[str] = Query(None),
        sort_by: LeadSortBy = Query(LeadSortBy.CREATED_AT),
        sort_order: SortOrder = Query(SortOrder.DESC),
        service: LeadService = Depends(get_lead_service)
):
    query_params = LeadGetQuery(
        page=page,
        limit=limit,
        status=status,
        source=source,
        assigned_to=assigned_to,
        date_from=date_from,
        date_to=date_to,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    data = await service.find_all_leads(query_params=query_params)
    return ResponseModel(data=LeadListResponse(**data))


# GET LEAD BY ID
@router.get(
    "/{lead_id}",
    response_model=ResponseModel[LeadResponse],
    dependencies=[Depends(auth_require)]
)
async def get_lead_by_id(lead_id: UUID, service: LeadService = Depends(get_lead_service)):
    data = await service.find_one_lead(lead_id)
    return ResponseModel(data=data)


# UPDATE LEAD
@router.put(
    "/{lead_id}",
    response_model=ResponseModel[LeadResponse],
    dependencies=[Depends(auth_require)]
)
async def update_lead_by_id(lead_id: UUID, payload: LeadRequest, service: LeadService = Depends(get_lead_service)):
    data = await service.update_lead(lead_id, payload)
    return ResponseModel(data=data)


# UPDATE LEAD STATUS
@router.patch(
    "/{lead_id}/status",
    response_model=ResponseModel[LeadResponse],
    dependencies=[Depends(auth_require)]
)
async def update_lead_status_by_id(
        lead_id: UUID,
        payload: LeadUpdateStatus,
        service: LeadService = Depends(get_lead_service)
):
    data = await service.update_lead_status(lead_id, payload)
    return ResponseModel(data=data)
