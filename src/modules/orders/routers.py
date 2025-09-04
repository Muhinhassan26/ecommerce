from fastapi import APIRouter, Depends
from src.core.dependencies import JWTBearer
from src.modules.orders.controllers import admin_orders_router, user_orders_routers

api_router = APIRouter()

api_router.include_router(
    admin_orders_router,
    prefix="/admin",
    tags=["Admin Order"],
    dependencies=[Depends(JWTBearer())],
)


api_router.include_router(
    user_orders_routers,
    prefix="/users",
    tags=["User Order"],
    dependencies=[Depends(JWTBearer())],
)
