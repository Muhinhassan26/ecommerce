from typing import Annotated

from fastapi import Depends
from src.core.error.exceptions import NotFoundException, RequestError
from src.core.error.format_error import ERROR_MAPPER, NO_DATA
from src.core.helpers.enums import OrderStatus
from src.core.logger import logger
from src.core.schemas.common import FilterOptions, PaginatedResponse, QueryParams
from src.core.service.base_service import BaseService
from src.modules.orders.repository import OrderRepository
from src.modules.orders.schemas import OrderResponse
from src.modules.products.repository import ProductRepository


class OrderAdminService(BaseService):
    def __init__(
        self,
        order_repo: Annotated[OrderRepository, Depends(OrderRepository)],
        product_repo: Annotated[ProductRepository, Depends(ProductRepository)],
    ):
        self.order_repo = order_repo
        self.product_repo = product_repo

        self.logger = logger

    async def list_orders(
        self,
        query_params: QueryParams,
        user_id: int,
    ) -> PaginatedResponse[OrderResponse]:
        filters = {}
        if user_id is not None:
            filters["user_id"] = int(user_id)

        if query_params.filter_params:
            filters.update(query_params.filter_params)
        filter_options = FilterOptions(
            filters=filters,
            prefetch=("order_products",),
            distinct_on="id",
            sorting={"created_at": "desc"},
            pagination=query_params,
        )

        orders, total = await self.order_repo.paginate_filters(filter_options)
        return PaginatedResponse[OrderResponse](
            data=[OrderResponse.model_validate(order) for order in orders],
            meta=await self.setup_pagination_meta(
                total=total,
                page_size=query_params.page_size,
                page=query_params.page,
            ),
        )

    async def get_order_detail(self, order_id: int) -> OrderResponse:
        filter_options = FilterOptions(
            filters={"id": order_id}, prefetch=("order_products", "prod")
        )
        order = await self.order_repo.get_by_filed(filter_options)
        if not order:
            raise NotFoundException(message=ERROR_MAPPER[NO_DATA])
        for item in order.order_products:
            item.price = float(item.price)
            item.total_price = float(item.total_price)

        order.total_amount = float(order.total_amount)
        return OrderResponse.model_validate(order)

    async def update_order_status(self, order_id: int, status: OrderStatus) -> OrderResponse:
        filter_options = FilterOptions(
            filters={"id": order_id},
            prefetch=(
                "order_products",
                "order_products.product",
            ),
        )
        order = await self.order_repo.get_by_filed(filter_options)
        if not order:
            raise NotFoundException(message=ERROR_MAPPER[NO_DATA])
        if status == OrderStatus.APPROVED:
            for item in order.order_products:
                product = item.product
                product.stock -= item.quantity
                await self.product_repo.update_obj(
                    where={"id": product.id}, values={"stock": product.stock}
                )
        for item in order.order_products:
            item.price = float(item.price)
            item.total_price = float(item.total_price)

        order.total_amount = float(order.total_amount)
        if not order:
            raise NotFoundException(message=ERROR_MAPPER[NO_DATA])

        if order.status == status:
            raise RequestError()

        updated_order = await self.order_repo.update_obj(  # noqa: F841
            where=filter_options.filters, values={"status": status}
        )

        return OrderResponse.model_validate(order)
