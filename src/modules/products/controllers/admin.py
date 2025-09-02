from typing import Annotated

from fastapi import APIRouter, Depends
from src.core.dependencies import CommonQueryParam
from src.core.schemas.common import PaginatedResponse, QueryParams
from src.modules.products.schemas import ProductCreate, ProductResponse
from src.modules.products.services.admin import ProductAdminService

router = APIRouter(
    prefix="/products",
)


@router.get("/", response_model=PaginatedResponse[ProductResponse])
async def get_products(
    product_service: Annotated[ProductAdminService, Depends(ProductAdminService)],
    query_paramas: QueryParams = Depends(
        CommonQueryParam(filter_fields=["is_active", "category", "name"])
    ),
):
    return await product_service.get_products(query_params=query_paramas)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_by_id(
    product_id: int,
    product_service: Annotated[ProductAdminService, Depends(ProductAdminService)],
):
    return await product_service.get_product_by_id(product_id=product_id)


@router.post("/", response_model=ProductResponse)
async def create_product(
    product: ProductCreate,
    product_service: Annotated[ProductAdminService, Depends(ProductAdminService)],
):
    return await product_service.create_product(product_create=product)


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_update: ProductCreate,
    product_service: Annotated[ProductAdminService, Depends(ProductAdminService)],
):
    return await product_service.update_product(
        product_id=product_id, product_update=product_update
    )


@router.delete("/{product_id}", response_model=ProductResponse)
async def delete_product(
    product_id: int,
    product_service: Annotated[ProductAdminService, Depends(ProductAdminService)],
):
    return await product_service.delete_product(product_id=product_id)
