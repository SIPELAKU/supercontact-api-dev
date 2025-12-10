from datetime import datetime, timezone
from uuid import UUID

from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Product
from app.schemas import ProductRequest, ProductGetQuery


class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, product_id: UUID):
        query = select(Product).where(Product.id == product_id)
        return await self.db.scalar(query)

    async def create(self, payload: ProductRequest):
        product = Product(**payload.model_dump())
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)

        return await self.get_by_id(product_id=product.id)

    async def get_all(self, query_params: ProductGetQuery):
        query = select(Product)

        # GET ALL WITHOUT LIMIT
        if query_params.limit == 0:
            total_data = select(func.count()).select_from(query.subquery())
            total = await self.db.scalar(total_data)
            result = await self.db.scalars(query)
            products = result.all()

            return products, total

        # SEARCH NAME
        if query_params.search:
            query = query.where(Product.product_name.ilike(f"%{query_params.search}%"))

        total_data = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(total_data)

        # PAGINATION
        offset = (query_params.page - 1) * query_params.limit
        result = await self.db.scalars(query.offset(offset).limit(query_params.limit))
        products = result.all()

        return products, total

    async def update(self, product: Product, payload: ProductRequest):
        updated_data = payload.model_dump()

        for key, value in updated_data.items():
            setattr(product, key, value)
        product.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(product)

        return await self.get_by_id(product_id=product.id)

    async def delete(self, product: Product):
        await self.db.delete(product)
        await self.db.commit()
        await self.db.refresh(product)

        return await self.get_by_id(product_id=product.id)
