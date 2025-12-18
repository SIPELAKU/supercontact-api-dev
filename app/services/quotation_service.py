import base64
from math import ceil
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.exceptions import AppException
from app.models import QuotationStatus
from app.repositories import QuotationRepository
from app.schemas import ErrorCode, QuotationRequest
from app.schemas.quotation_schema import QuotationGetQuery
from app.utils import brevo_send_email


class QuotationService:
    def __init__(self, db: AsyncSession):
        self.repo = QuotationRepository(db)

    # GET QUOTATION BY ID
    async def find_one_quotation(self, quotation_id: UUID):
        quotation = await self.repo.get_by_id(quotation_id)
        if not quotation:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Quotation not found"
            )
        return quotation

    # CREATE NEW QUOTATION
    async def create_quotation(self, payload: QuotationRequest, status: QuotationStatus):
        return await self.repo.create(payload=payload, status=status)

    # GET ALL QUOTATIONS
    async def find_all_quotations(self, query_params: QuotationGetQuery):
        quotations, total = await self.repo.get_all(query_params=query_params)
        total_pages = ceil(total / query_params.limit)

        return {
            "total": total,
            "page": query_params.page,
            "limit": query_params.limit,
            "total_pages": total_pages,
            "quotations": quotations,
        }

    # UPDATE QUOTATION
    async def update_quotation(self, quotation_id: UUID, payload: QuotationRequest, status: QuotationStatus):
        quotation = await self.repo.get_by_id(quotation_id=quotation_id)
        if not quotation:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Quotation not found"
            )
        if quotation.status != QuotationStatus.PENDING:
            raise AppException(
                status_code=400,
                code=ErrorCode.VALIDATION_ERROR,
                message="Quotation status not pending"
            )

        return await self.repo.update(quotation=quotation, payload=payload, status=status)

    # SEND PDF BY EMAIL
    @staticmethod
    async def send_pdf_email(to_email: str, subject: str, filename: str, pdf_bytes: bytes):
        encoded_file = base64.b64encode(pdf_bytes).decode("utf-8")

        payload = {
            "sender": {
                "email": "afifu5882@gmail.com",
                "name": "Sales",
            },
            "to": [{"email": to_email}],
            "subject": subject or "PDF Document",
            "htmlContent": """
                    <p>Hello,</p>
                    <p>Please find the attached PDF document.</p>
                """,
            "attachment": [
                {
                    "content": encoded_file,
                    "name": filename,
                }
            ],
        }
        await brevo_send_email(payload=payload)

        return {
            "to_email": to_email,
            "subject": subject,
            "delivered": True,
        }
