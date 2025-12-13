from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_async_session
from app.schemas import (
    ResponseModel,
    ProductGetQuery,
    ProductListResponse,
    ProductResponse, ProductRequest, ProductDeleteResponse,
)
from app.services import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


def get_product_service(db: AsyncSession = Depends(get_async_session)):
    return ProductService(db)


# GET ALL PRODUCTS
@router.get(
    "",
    response_model=ResponseModel[ProductListResponse],
    # dependencies=[Depends(auth_require)],
)
async def get_all_products(
        query_params: ProductGetQuery = Depends(),
        service: ProductService = Depends(get_product_service)
):
    data = await service.find_all_products(query_params=query_params)
    return ResponseModel(data=ProductListResponse(**data))


# CREATE NEW PRODUCT
@router.post(
    "",
    response_model=ResponseModel[ProductResponse],
    #     dependencies=[Depends(auth_require)],
)
async def create_new_product(
        payload: ProductRequest,
        service: ProductService = Depends(get_product_service)
):
    data = await service.create_product(payload=payload)
    return ResponseModel(data=data)


# GET PRODUCT BY ID
@router.get(
    "/{product_id}",
    response_model=ResponseModel[ProductResponse],
    #     dependencies=[Depends(auth_require)],
)
async def get_product_by_id(
        product_id: UUID,
        service: ProductService = Depends(get_product_service)
):
    data = await service.find_one_product(product_id=product_id)
    return ResponseModel(data=data)


# UPDATE PRODUCT BY ID
@router.put(
    "/{product_id}",
    response_model=ResponseModel[ProductResponse],
    #     dependencies=[Depends(auth_require)],
)
async def update_product_by_id(
        product_id: UUID,
        payload: ProductRequest,
        service: ProductService = Depends(get_product_service)
):
    data = await service.update_product(product_id=product_id, payload=payload)
    return ResponseModel(data=data)


# DELETE PRODUCT BY ID
@router.delete(
    "/{product_id}",
    response_model=ResponseModel[ProductDeleteResponse],
    #     dependencies=[Depends(auth_require)],
)
async def delete_product_by_id(
        product_id: UUID,
        service: ProductService = Depends(get_product_service)
):
    data = await service.delete_product(product_id=product_id)
    return ResponseModel(data=ProductDeleteResponse(id=product_id, deleted=data))
