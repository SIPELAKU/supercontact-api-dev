from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_async_session
from app.models import LeadSource, LeadStatus
from app.schemas import (
    LeadRequest,
    LeadResponse,
    LeadListResponse,
    ResponseModel,
    LeadUpdateStatus,
    LeadDeleteResponse,
    SortOrder,
    LeadGetQuery,
)
from app.services import LeadService
from app.utils.permissions import require_permissions

router = APIRouter(prefix="/leads", tags=["Leads"])


# =========================
# Dependency
# =========================
def get_lead_service(
    db: AsyncSession = Depends(get_async_session),
):
    return LeadService(db)


# =========================
# GET ALL LEADS
# =========================
@router.get(
    "",
    response_model=ResponseModel[LeadListResponse],
    # dependencies=[Depends(require_permissions("lead:view"))],
)
async def get_all_leads(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    lead_status: Optional[List[LeadStatus]] = Query(None),
    lead_source: Optional[List[LeadSource]] = Query(None),
    assigned_to: Optional[List[UUID]] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    search: Optional[str] = Query(None),
    sort_order: SortOrder = Query(SortOrder.DESC),
    service: LeadService = Depends(get_lead_service),
):
    query_params = LeadGetQuery(
        page=page,
        limit=limit,
        lead_status=lead_status,
        lead_source=lead_source,
        assigned_to=assigned_to,
        date_from=date_from,
        date_to=date_to,
        search=search,
        sort_order=sort_order,
    )

    data = await service.find_all_leads(query_params=query_params)
    return ResponseModel(data=LeadListResponse(**data))


# =========================
# CREATE NEW LEAD
# =========================
@router.post(
    "",
    response_model=ResponseModel[LeadResponse],
    # dependencies=[Depends(require_permissions("lead:create"))],
)
async def create_lead(
    payload: LeadRequest,
    service: LeadService = Depends(get_lead_service),
):
    data = await service.create_lead(payload)
    return ResponseModel(data=data)


# =========================
# GET LEAD BY ID
# =========================
@router.get(
    "/{lead_id}",
    response_model=ResponseModel[LeadResponse],
    dependencies=[Depends(require_permissions("lead:view"))],
)
async def get_lead_by_id(
    lead_id: UUID,
    service: LeadService = Depends(get_lead_service),
):
    data = await service.find_one_lead(lead_id)
    return ResponseModel(data=data)


# =========================
# UPDATE LEAD
# =========================
@router.put(
    "/{lead_id}",
    response_model=ResponseModel[LeadResponse],
    # dependencies=[Depends(require_permissions("lead:update"))],
)
async def update_lead_by_id(
    lead_id: UUID,
    payload: LeadRequest,
    service: LeadService = Depends(get_lead_service),
):
    data = await service.update_lead(lead_id, payload)
    return ResponseModel(data=data)


# =========================
# DELETE LEAD
# =========================
@router.delete(
    "/{lead_id}",
    response_model=ResponseModel[LeadDeleteResponse],
    # dependencies=[Depends(require_permissions("lead:delete"))],
)
async def delete_lead_status_by_id(
    lead_id: UUID,
    service: LeadService = Depends(get_lead_service),
):
    deleted = await service.delete_lead(lead_id=lead_id)
    return ResponseModel(
        data=LeadDeleteResponse(
            id=lead_id,
            deleted=deleted,
        )
    )


# =========================
# UPDATE LEAD STATUS
# =========================
@router.patch(
    "/{lead_id}/status",
    response_model=ResponseModel[LeadResponse],
    # dependencies=[Depends(require_permissions("lead:status:update"))],
)
async def update_lead_status_by_id(
    lead_id: UUID,
    payload: LeadUpdateStatus,
    service: LeadService = Depends(get_lead_service),
):
    data = await service.update_lead_status(lead_id, payload)
    return ResponseModel(data=data)
