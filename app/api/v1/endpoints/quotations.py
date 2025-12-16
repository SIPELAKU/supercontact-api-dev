from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import get_db_session
from app.models import QuotationStatus
from app.schemas import ResponseModel, QuotationResponse, QuotationListResponse, QuotationRequest
from app.schemas.quotation_schema import QuotationGetQuery, QuotationDeleteResponse
from app.services import QuotationService

router = APIRouter(prefix="/quotations", tags=["Quotations"])


async def get_quotation_service(db: AsyncSession = Depends(get_db_session)):
    return QuotationService(db=db)


@router.get(
    "",
    # dependencies=[Depends(auth_require)],
    response_model=ResponseModel[QuotationListResponse],
)
async def get_all_quotations(
        query_params: QuotationGetQuery = Depends(),
        service: QuotationService = Depends(get_quotation_service),
):
    data = await service.find_all_quotations(query_params=query_params)
    return ResponseModel(data=data)


# CREATE NEW QUOTATION (SAVE AS DRAFT)
@router.post(
    "",
    response_model=ResponseModel[QuotationResponse],
    #     dependencies=[Depends(auth_require)],
)
async def create_new_quotation_as_draft(
        payload: QuotationRequest,
        service: QuotationService = Depends(get_quotation_service)
):
    data = await service.create_quotation(payload=payload, status=QuotationStatus.PENDING)
    return ResponseModel(data=data)


# CREATE NEW QUOTATION
@router.post(
    "",
    response_model=ResponseModel[QuotationResponse],
    #     dependencies=[Depends(auth_require)],
)
async def create_new_quotation_as_publish(
        payload: QuotationRequest,
        service: QuotationService = Depends(get_quotation_service)
):
    data = await service.create_quotation(payload=payload, status=QuotationStatus.PENDING)
    return ResponseModel(data=data)


# GET QUOTATION BY ID
@router.get(
    "/{quotation_id}",
    response_model=ResponseModel[QuotationResponse],
    #     dependencies=[Depends(auth_require)],
)
async def get_quotation_by_id(
        quotation_id: UUID,
        service: QuotationService = Depends(get_quotation_service)
):
    data = await service.find_one_quotation(quotation_id=quotation_id)
    return ResponseModel(data=data)


# UPDATE QUOTATION BY ID
@router.put(
    "/{quotation_id}",
    response_model=ResponseModel[QuotationResponse],
    #     dependencies=[Depends(auth_require)],
)
async def update_quotation_by_id(
        quotation_id: UUID,
        payload: QuotationRequest,
        service: QuotationService = Depends(get_quotation_service)
):
    data = await service.update_quotation(quotation_id=quotation_id, payload=payload)
    return ResponseModel(data=data)


# DELETE QUOTATION BY ID
@router.delete(
    "/{quotation_id}",
    response_model=ResponseModel[QuotationDeleteResponse],
    #     dependencies=[Depends(auth_require)],
)
async def delete_quotation_by_id(
        quotation_id: UUID,
        service: QuotationService = Depends(get_quotation_service)
):
    data = await service.delete_quotation(quotation_id=quotation_id)
    return ResponseModel(data=QuotationDeleteResponse(id=quotation_id, deleted=data))
