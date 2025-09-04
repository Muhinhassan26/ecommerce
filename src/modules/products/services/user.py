from typing import Annotated

from fastapi import Depends
from src.core.error.codes import NO_DATA
from src.core.error.exceptions import NotFoundException
from src.core.error.format_error import ERROR_MAPPER
from src.core.logger import logger
from src.core.schemas.common import FilterOptions, PaginatedResponse, QueryParams
from src.core.service.base_service import BaseService
from src.modules.products.repository import ProductRepository
from src.modules.products.schemas import ProductResponse


class ProductUserService(BaseService):
    def __init__(self, product_repo: Annotated[ProductRepository, Depends(ProductRepository)]):
        self.product_repo = product_repo
        self.logger = logger

    async def get_product_by_id(self, product_id: int, user_id: int) -> ProductResponse | None:
        filter_options = FilterOptions(
            filters={
                "user_id": user_id,
            }
        )
        product = await self.product_repo.filter(obj_id=product_id, filter_options=filter_options)

        if not product:
            logger.error(msg=f"Product with id {product_id} is not available")
            raise NotFoundException(message=ERROR_MAPPER[NO_DATA])

        return ProductResponse.model_validate(product)

    async def get_paginate_product(
        self,
        user_id,
        query_params: QueryParams,
    ) -> PaginatedResponse[ProductResponse]:
        filters = {"user_id": user_id}

        if query_params.filter_params:
            filters.update(query_params.filter_params)

        filter_options = FilterOptions(
            filters=filters,
            pagination=query_params,
            sorting={"created_at": "desc"},
            search_fields=["name", "description"],
        )
        products, total = await self.product_repo.paginate_filters(filter_options=filter_options)

        if total == 0:
            logger.error(msg="No products available")
            raise NotFoundException(message=ERROR_MAPPER[NO_DATA])

        return PaginatedResponse(
            data=products,
            meta=self.setup_pagination_meta(
                total=total,
                page_size=query_params.page_size,
                page=query_params.page,
            ),
        )
