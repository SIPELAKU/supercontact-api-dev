from datetime import timezone, datetime
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import select, func, or_
from sqlmodel.ext.asyncio.session import AsyncSession

from app.exceptions import AppException
from app.models import Quotation, Lead, QuotationItem, Contact, Product
from app.schemas import QuotationRequest, ErrorCode
from app.schemas.quotation_schema import QuotationGetQuery


class QuotationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, quotation_id: UUID):
        query = (
            select(Quotation)
            .where(Quotation.id == quotation_id)
            .options(
                selectinload(Quotation.items).options(
                    selectinload(QuotationItem.product)
                ),
                selectinload(Quotation.lead).options(
                    selectinload(Lead.contact)
                )
            )
        )
        return await self.db.scalar(query)

    async def get_product_by_id(self, product_id: UUID):
        return await self.db.scalar(select(Product).where(Product.id == product_id))

    async def create(self, payload: QuotationRequest):
        grand_total = 0
        quotation = Quotation(
            lead_id=payload.lead_id,
            quotation_title=payload.quotation_title,
            expire_date=payload.expire_date,
            grand_total=grand_total,
        )

        self.db.add(quotation)
        await self.db.flush()

        # ADD QUOTATION ITEMS
        for item in payload.items:
            product = await self.get_product_by_id(item.product_id)
            if not product:
                raise AppException(status_code=404, code=ErrorCode.NOT_FOUND, message="Product not found")

            unit_price = product.price
            subtotal = unit_price * item.quantity
            grand_total += subtotal

            quotation_item = QuotationItem(
                quotation_id=quotation.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=unit_price,
                subtotal=subtotal,
                notes=item.notes,
            )
            self.db.add(quotation_item)

        # UPDATE GRAND TOTAL
        quotation.grand_total = grand_total

        await self.db.commit()
        await self.db.refresh(quotation)

        return await self.get_by_id(quotation_id=quotation.id)

    async def get_all(self, query_params: QuotationGetQuery):
        query = (
            select(Quotation)
            .join(Quotation.lead)
            .join(Lead.contact)
            .options(
                selectinload(Quotation.items).options(
                    selectinload(QuotationItem.product)
                ),
                selectinload(Quotation.lead).options(
                    selectinload(Lead.contact)
                )
            )
        )

        # SEARCH NAME
        if query_params.search:
            search = f'%{query_params.search}%'
            query = query.where(
                or_(
                    Contact.name.ilike(search),
                    Contact.company.ilike(search),
                )
            )

        # COUNT
        total_data = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(total_data)

        # PAGINATION
        offset = (query_params.page - 1) * query_params.limit
        result = await self.db.scalars(query.offset(offset).limit(query_params.limit))
        quotations = result.all()

        return quotations, total

    async def update(self, quotation: Quotation, payload: QuotationRequest):
        grand_total = 0
        # UPDATE FIELD PARENT
        quotation.lead_id = payload.lead_id
        quotation.quotation_title = payload.quotation_title
        quotation.expire_date = payload.expire_date

        old_items = await self.db.scalars(
            select(QuotationItem)
            .where(QuotationItem.quotation_id == quotation.id)
        )
        old_items = old_items.all()
        # DELETE OLD ITEMS
        for item in old_items:
            await self.db.delete(item)
        await self.db.flush()

        # INSERT NEW ITEMS
        for item in payload.items:
            product = await self.get_product_by_id(item.product_id)
            if not product:
                raise AppException(status_code=404, code=ErrorCode.NOT_FOUND, message="Product not found")

            unit_price = product.price
            subtotal = unit_price * item.quantity
            grand_total += subtotal

            quotation_item = QuotationItem(
                quotation_id=quotation.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=unit_price,
                subtotal=subtotal,
                notes=item.notes,
            )
            self.db.add(quotation_item)

        quotation.grand_total = grand_total
        quotation.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(quotation)
        return await self.get_by_id(quotation_id=quotation.id)

    async def delete(self, quotation: Quotation):
        await self.db.delete(quotation)
        await self.db.commit()

        return True
