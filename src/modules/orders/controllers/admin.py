from typing import Annotated

from fastapi import APIRouter, Depends
from src.core.dependencies import CommonQueryParam
from src.core.helpers.enums import OrderStatus
from src.core.schemas.common import PaginatedResponse, QueryParams
from src.modules.orders.schemas import OrderResponse
from src.modules.orders.services.admin import OrderAdminService

router = APIRouter(prefix="/admin/orders")


@router.get("/", response_model=PaginatedResponse[OrderResponse])
async def list_orders(
    query_params: QueryParams = Depends(
        CommonQueryParam(filter_fields=["status", "user_id", "created_at"])
    ),
    service: Annotated[OrderAdminService, Depends(OrderAdminService)] = Depends(),
):
    return await service.list_orders(
        query_params=query_params, user_id=query_params.filter_params.get("user_id")
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_detail(
    order_id: int,
    service: Annotated[OrderAdminService, Depends(OrderAdminService)],
):
    return await service.get_order_detail(order_id=order_id)


@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    status: OrderStatus,
    service: Annotated[OrderAdminService, Depends(OrderAdminService)],
):
    return await service.update_order_status(order_id=order_id, status=status)
