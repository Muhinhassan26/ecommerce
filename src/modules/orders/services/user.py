from typing import Annotated

from fastapi import Depends
from src.core.error.exceptions import NotFoundException, RequestError
from src.core.error.format_error import ERROR_MAPPER, NO_DATA
from src.core.helpers.enums import OrderStatus
from src.core.logger import logger
from src.core.schemas.common import FilterOptions, PaginatedResponse, QueryParams
from src.core.service.base_service import BaseService
from src.modules.orders.models import Order, OrderProduct
from src.modules.orders.repository import OrderRepository
from src.modules.orders.schemas import (
    OrderCreate,
    OrderResponse,
)
from src.modules.products.repository import ProductRepository


class OrderUserService(BaseService):
    def __init__(
        self,
        order_repo: Annotated[OrderRepository, Depends(OrderRepository)],
        product_repo: Annotated[ProductRepository, Depends(ProductRepository)],
    ):
        self.order_repo = order_repo
        self.product_repo = product_repo
        self.logger = logger

    async def create_order(self, user_id: int, create_order: OrderCreate) -> OrderResponse:
        total_amount: float = 0.0
        order_products: list[OrderProduct] = []

        for item in create_order.items:
            product = await self.product_repo.get_by_id(obj_id=item.product_id)
            if not product:
                raise NotFoundException(message=ERROR_MAPPER[NO_DATA])
            if product.stock < item.quantity:
                raise RequestError(
                    message=f"Not enough stock for product '{product.name}'. "
                    f"Available: {product.stock}, Requested: {item.quantity}"
                )

            price = float(product.price)
            total_price = price * float(item.quantity)

            total_amount += total_price
            order_products.append(
                OrderProduct(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=price,
                    total_price=total_price,
                )
            )
        order = Order(user_id=user_id, total_amount=total_amount, status=OrderStatus.PENDING)
        order.order_products = order_products

        created_order = await self.order_repo.create(order)
        created_order = await self.order_repo.get_by_id(
            obj_id=created_order.id, filter_options=FilterOptions(prefetch=("order_products",))
        )

        return OrderResponse.model_validate(created_order)

    async def get_my_orders(
        self, query_params: QueryParams, user_id: int
    ) -> PaginatedResponse[OrderResponse]:
        filters = {"user_id": user_id}
        if query_params.filter_params:
            filters.update(query_params.filter_params)
        filter_options = FilterOptions(
            filters=filters,
            distinct_on="id",
            prefetch=("order_products",),
            sorting={"created_at": "desc"},
            pagination=query_params,
        )

        orders, total = await self.order_repo.paginate_filters(filter_options)
        return PaginatedResponse[OrderResponse](
            data=[OrderResponse.model_validate(order) for order in orders],
            meta=await self.setup_pagination_meta(
                total=total, page_size=query_params.page_size, page=query_params.page
            ),
        )

    async def get_order_detail(self, user_id: int, order_id: int) -> OrderResponse:
        filter_options = FilterOptions(
            filters={"id": order_id, "user_id": user_id}, prefetch=("order_products",)
        )

        order = await self.order_repo.get_by_filed(filter_options)
        if not order:
            raise NotFoundException(message=ERROR_MAPPER[NO_DATA])

        return OrderResponse.model_validate(order)

    async def cancel_order(self, user_id: int, order_id: int) -> OrderResponse:
        filter_options = FilterOptions(
            filters={"id": order_id, "user_id": user_id}, prefetch=("order_products",)
        )
        order = await self.order_repo.get_by_filed(filter_options)
        if not order:
            raise NotFoundException(message=ERROR_MAPPER[NO_DATA])

        if order.status != OrderStatus.PENDING:
            raise RequestError()

        updated_order = await self.order_repo.update_obj(
            where=filter_options.filters, values={"status": OrderStatus.CANCELLED}
        )

        updated_order = await self.order_repo.get_by_id(
            order_id, filter_options=FilterOptions(prefetch=("order_products",))
        )
        return OrderResponse.model_validate(updated_order)
