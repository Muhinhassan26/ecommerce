from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from src.core.decorators import check_user_perm
from src.core.dependencies import CommonQueryParam
from src.core.helpers.enums import OrderStatus, UserRole
from src.core.schemas.common import PaginatedResponse, QueryParams
from src.modules.orders.schemas import OrderResponse
from src.modules.orders.services.admin import OrderAdminService

router = APIRouter(prefix="/orders")


@router.get("/", response_model=PaginatedResponse[OrderResponse])
@check_user_perm([UserRole.ORDER_MANAGER.value, UserRole.SUPER_ADMIN.value])
async def list_orders(
    request: Request,  # noqa: ARG001
    service: Annotated[OrderAdminService, Depends(OrderAdminService)],
    query_params: QueryParams = Depends(
        CommonQueryParam(filter_fields=["status", "user_id", "created_at"])
    ),
) -> Any:
    return await service.list_orders(
        query_params=query_params, user_id=query_params.filter_params.get("user_id")
    )


@router.get("/{order_id}", response_model=OrderResponse)
@check_user_perm([UserRole.ORDER_MANAGER.value])
async def get_order_detail(
    request: Request,  # noqa: ARG001
    order_id: int,
    service: Annotated[OrderAdminService, Depends(OrderAdminService)],
) -> Any:
    return await service.get_order_detail(order_id=order_id)


@router.patch("/{order_id}/status", response_model=OrderResponse)
@check_user_perm([UserRole.ORDER_MANAGER.value])
async def update_order_status(
    request: Request,  # noqa: ARG001
    order_id: int,
    status: OrderStatus,
    service: Annotated[OrderAdminService, Depends(OrderAdminService)],
) -> Any:
    return await service.update_order_status(order_id=order_id, status=status)
