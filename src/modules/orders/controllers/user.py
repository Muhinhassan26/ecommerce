from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from src.core.dependencies import CommonQueryParam
from src.core.schemas.common import PaginatedResponse, QueryParams
from src.modules.orders.schemas import OrderCreate, OrderResponse
from src.modules.orders.services.user import OrderUserService

router = APIRouter(prefix="/orders")


@router.post("/", response_model=OrderResponse)
async def create_order(
    request: Request,
    create_order: OrderCreate,
    service: Annotated[OrderUserService, Depends(OrderUserService)],
) -> Any:
    user_id = request.state.user_id
    return await service.create_order(user_id=user_id, create_order=create_order)


@router.get("/", response_model=PaginatedResponse[OrderResponse])
async def get_my_orders(
    request: Request,
    service: Annotated[OrderUserService, Depends(OrderUserService)],
    query_params: QueryParams = Depends(
        CommonQueryParam(filter_fields=["search", "created_at", "status"])
    ),
) -> Any:
    user_id = request.state.user_id
    return await service.get_my_orders(query_params=query_params, user_id=user_id)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_detail(
    request: Request,
    order_id: int,
    service: Annotated[OrderUserService, Depends(OrderUserService)],
) -> Any:
    user_id = request.state.user_id
    return await service.get_order_detail(user_id=user_id, order_id=order_id)


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    request: Request,
    order_id: int,
    service: Annotated[OrderUserService, Depends(OrderUserService)],
) -> Any:
    user_id = request.state.user_id
    return await service.cancel_order(user_id=user_id, order_id=order_id)
