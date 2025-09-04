from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from src.core.dependencies import CommonQueryParam
from src.core.schemas.common import PaginatedResponse, QueryParams
from src.modules.products.schemas import ProductResponse
from src.modules.products.services.user import ProductUserService

router = APIRouter(
    prefix="/products",
)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_by_id(
    request: Request,
    product_id: int,
    product_service: Annotated[ProductUserService, Depends(ProductUserService)],
) -> Any:
    user_id = request.state.user_id
    return await product_service.get_product_by_id(product_id=product_id, user_id=user_id)


@router.get("/", response_model=PaginatedResponse[ProductResponse])
async def get_products_paginated(
    request: Request,
    product_service: Annotated[ProductUserService, Depends(ProductUserService)],
    query_params: QueryParams = Depends(
        CommonQueryParam(filter_fields=["search", "is_active", "category", "name"])
    ),
) -> Any:
    user_id = request.state.user_id
    return await product_service.get_paginate_product(user_id=user_id, query_params=query_params)
