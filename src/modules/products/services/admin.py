from typing import Annotated

from fastapi import Depends
from src.core.error.codes import NO_DATA
from src.core.error.exceptions import NotFoundException
from src.core.error.format_error import ERROR_MAPPER
from src.core.logger import logger
from src.core.schemas.common import FilterOptions, PaginatedResponse, QueryParams
from src.core.service.base_service import BaseService
from src.modules.products.models import Product
from src.modules.products.repository import ProductRepository
from src.modules.products.schemas import ProductCreate, ProductResponse, ProductUpdate


class ProductAdminService(BaseService):
    def __init__(self, product_repo: Annotated[ProductRepository, Depends(ProductRepository)]):
        self.product_repo = product_repo
        self.logger = logger

    async def get_all_products(self) -> list[ProductResponse]:
        filter_options = FilterOptions(sorting={"created_at": "desc"})
        return await self.product_repo.filter(filter_options=filter_options)

    async def get_paginate_product(
        self,
        query_params: QueryParams,
    ) -> PaginatedResponse[ProductResponse]:
        filter_options = FilterOptions(
            pagination=query_params,
            sorting={"created_at": "desc"},
            search_fields=["name", "description"],
        )
        products, total = self.product_repo.paginate_filters(filter_options=filter_options)

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

    async def get_product_by_id(
        self,
        product_id: int,
    ) -> ProductResponse | None:
        product = await self.product_repo.get_by_id(obj_id=product_id)

        if not product:
            logger.error(msg=f"Product with id {product_id} is not available")
            raise NotFoundException(message=ERROR_MAPPER[NO_DATA])

        return product

    async def create_product(
        self,
        create_product: ProductCreate,
    ) -> ProductCreate:
        new_product = self.product_repo.create(obj=Product(**create_product.model_dump()))
        self.logger.info(f"Product created: product_id={new_product.id}")
        return new_product

    async def update_product(self, product_id: int, update_product: ProductUpdate) -> ProductUpdate:
        filters = {"id": product_id}

        updated, total = self.product_repo.update_obj(
            where=filters, values=update_product.model_dump(exclude_none=True)
        )

        if total == 0:
            self.logger.warning(f"Product update failed: product_id={product_id}")
            raise NotFoundException(message=ERROR_MAPPER[NO_DATA])

        self.logger.info(f"Product updated: product_id={product_id}")
        return updated

    async def delete_product(self, product_id: int) -> None:
        filters = {"id": product_id}

        filter_options = FilterOptions(filters=filters)
        return await self.product_repo.delete(filter_options=filter_options)
