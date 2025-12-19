from math import ceil
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.exceptions import AppException
from app.repositories import ProductRepository
from app.schemas import ProductRequest, ProductGetQuery, ErrorCode


class ProductService:
    def __init__(self, db: AsyncSession):
        self.repo = ProductRepository(db=db)

    # CREATE NEW PRODUCT
    async def create_product(self, payload: ProductRequest):
        return await self.repo.create(payload=payload)

    # GET PRODUCT BY ID
    async def find_one_product(self, product_id: UUID):
        product = await self.repo.get_by_id(product_id=product_id)
        if not product:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Product not found"
            )
        return product

    # GET ALL PRODUCTS
    async def find_all_products(self, query_params: ProductGetQuery):
        products, total = await self.repo.get_all(query_params=query_params)
        total_pages = ceil(total / query_params.limit)

        return {
            "total": total,
            "page": query_params.page,
            "limit": query_params.limit,
            "total_pages": total_pages,
            "products": products,
        }

    # UPDATE PRODUCT
    async def update_product(self, product_id: UUID, payload: ProductRequest):
        product = await  self.repo.get_by_id(product_id=product_id)
        if not product:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Product not found"
            )

        return await self.repo.update(product=product, payload=payload)

    # DELETE PRODUCT
    async def delete_product(self, product_id: UUID):
        product = await  self.repo.get_by_id(product_id=product_id)
        if not product:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Product not found"
            )

        return await self.repo.delete(product=product)
