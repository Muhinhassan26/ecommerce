from typing import Annotated, Any

from fastapi import APIRouter, Depends
from src.core.dependencies import CommonQueryParam
from src.core.schemas.common import PaginatedResponse, QueryParams
from src.modules.products.schemas import ProductResponse
from src.modules.products.services.user import ProductUserService

router = APIRouter(
    prefix="/products",
)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_by_id(
    product_id: int,
    product_service: Annotated[ProductUserService, Depends(ProductUserService)],
) -> Any:
    return await product_service.get_product_by_id(product_id=product_id)


@router.get("/", response_model=PaginatedResponse[ProductResponse])
async def get_products_paginated(
    product_service: Annotated[ProductUserService, Depends(ProductUserService)],
    query_params: QueryParams = Depends(
        CommonQueryParam(filter_fields=["search", "is_active", "category", "name"])
    ),
) -> Any:
    return await product_service.get_paginate_product(query_params=query_params)
