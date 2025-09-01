from typing import Annotated

from fastapi import Depends
from src.core.error.exceptions import NotFoundException, RequestError
from src.core.error.format_error import ERROR_MAPPER, NO_DATA
from src.core.helpers.enums import OrderStatus
from src.core.logger import logger
from src.core.schemas.common import FilterOptions
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
    ):
        self.order_repo = order_repo
        self.logger = logger

    async def create_order(self, user_id: int, create_order: OrderCreate) -> OrderResponse:
        total_amount = 0
        order_products: list[OrderProduct] = []

        for item in create_order.items:
            product = await ProductRepository.get_by_id(obj_id=item.product_id)
            if not product:
                raise NotFoundException(message=ERROR_MAPPER[NO_DATA])

            price = float(product.price)
            total_price = price * item.quantity

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
        return OrderResponse.model_validate(created_order)

    async def get_my_orders(self, user_id: int) -> list[OrderResponse]:
        filter_options = FilterOptions(
            filters={"user_id": user_id},
            distinct_on="id",
            prefetch=("order_products",),
            sorting={"created_at": "desc"},
        )

        orders = await self.order_repo.filter(filter_options)
        return [OrderResponse.model_validate(order) for order in orders]

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

        updated_order, _ = await self.order_repo.update_obj(
            where=filter_options.filters, values={"status": OrderStatus.CANCELLED}
        )

        return OrderResponse.model_validate(updated_order)
