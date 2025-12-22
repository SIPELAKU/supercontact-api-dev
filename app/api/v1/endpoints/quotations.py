from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import get_db_session
from app.exceptions import AppException
from app.models import QuotationStatus
from app.schemas import (
    ResponseModel,
    QuotationResponse,
    QuotationListResponse,
    QuotationRequest,
    ErrorCode,
    QuotationSendEmailResponse,
)
from app.schemas.quotation_schema import QuotationGetQuery
from app.services import QuotationService
from app.utils.permissions import require_permissions

router = APIRouter(prefix="/quotations", tags=["Quotations"])


# =========================
# Dependency
# =========================
async def get_quotation_service(
    db: AsyncSession = Depends(get_db_session),
):
    return QuotationService(db=db)


# =========================
# GET ALL QUOTATIONS
# =========================
@router.get(
    "",
    response_model=ResponseModel[QuotationListResponse],
    dependencies=[Depends(require_permissions("quotation:view"))],
)
async def get_all_quotations(
    query_params: QuotationGetQuery = Depends(),
    service: QuotationService = Depends(get_quotation_service),
):
    data = await service.find_all_quotations(query_params=query_params)
    return ResponseModel(data=data)


# =========================
# CREATE NEW QUOTATION (DRAFT)
# =========================
@router.post(
    "/draft",
    response_model=ResponseModel[QuotationResponse],
    dependencies=[Depends(require_permissions("quotation:create"))],
)
async def create_new_quotation_as_draft(
    payload: QuotationRequest,
    service: QuotationService = Depends(get_quotation_service),
):
    data = await service.create_quotation(
        payload=payload,
        status=QuotationStatus.PENDING,
    )
    return ResponseModel(data=data)


# =========================
# CREATE NEW QUOTATION (PUBLISH)
# =========================
@router.post(
    "/publish",
    response_model=ResponseModel[QuotationResponse],
    dependencies=[Depends(require_permissions("quotation:publish"))],
)
async def create_new_quotation_as_publish(
    payload: QuotationRequest,
    service: QuotationService = Depends(get_quotation_service),
):
    data = await service.create_quotation(
        payload=payload,
        status=QuotationStatus.ACCEPTED,
    )
    return ResponseModel(data=data)


# =========================
# GET QUOTATION BY ID
# =========================
@router.get(
    "/{quotation_id}",
    response_model=ResponseModel[QuotationResponse],
    dependencies=[Depends(require_permissions("quotation:view"))],
)
async def get_quotation_by_id(
    quotation_id: UUID,
    service: QuotationService = Depends(get_quotation_service),
):
    data = await service.find_one_quotation(quotation_id=quotation_id)
    return ResponseModel(data=data)


# =========================
# UPDATE QUOTATION (DRAFT)
# =========================
@router.put(
    "/{quotation_id}/draft",
    response_model=ResponseModel[QuotationResponse],
    dependencies=[Depends(require_permissions("quotation:update"))],
)
async def update_quotation_by_id_as_draft(
    quotation_id: UUID,
    payload: QuotationRequest,
    service: QuotationService = Depends(get_quotation_service),
):
    data = await service.update_quotation(
        quotation_id=quotation_id,
        payload=payload,
        status=QuotationStatus.PENDING,
    )
    return ResponseModel(data=data)


# =========================
# UPDATE QUOTATION (PUBLISH)
# =========================
@router.put(
    "/{quotation_id}/publish",
    response_model=ResponseModel[QuotationResponse],
    dependencies=[Depends(require_permissions("quotation:publish"))],
)
async def update_quotation_by_id_as_publish(
    quotation_id: UUID,
    payload: QuotationRequest,
    service: QuotationService = Depends(get_quotation_service),
):
    data = await service.update_quotation(
        quotation_id=quotation_id,
        payload=payload,
        status=QuotationStatus.ACCEPTED,
    )
    return ResponseModel(data=data)


# =========================
# SEND QUOTATION VIA EMAIL
# =========================
@router.post(
    "/send-email",
    response_model=ResponseModel[QuotationSendEmailResponse],
    dependencies=[Depends(require_permissions("quotation:send_email"))],
)
async def send_to_quotation_by_email(
    to_email: str = Form(...),
    subject: str = Form(...),
    file: UploadFile = File(...),
    service: QuotationService = Depends(get_quotation_service),
):
    if file.content_type != "application/pdf":
        raise AppException(
            code=ErrorCode.VALIDATION_ERROR,
            status_code=400,
            message="Only PDF files are allowed",
        )

    pdf_bytes = await file.read()

    if len(pdf_bytes) > 5 * 1024 * 1024:
        raise AppException(
            code=ErrorCode.VALIDATION_ERROR,
            status_code=400,
            message="File size must be under 5MB",
        )

    data = await service.send_pdf_email(
        to_email=to_email,
        pdf_bytes=pdf_bytes,
        filename=file.filename,
        subject=subject,
    )

    return ResponseModel(data=data)
