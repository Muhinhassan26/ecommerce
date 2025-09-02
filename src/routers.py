from fastapi import APIRouter
from src.modules.auth.routers import api_router as auth_router
from src.modules.orders.routers import api_router as order_router
from src.modules.products.routers import api_router as product_router
from src.modules.users.routers import api_router as user_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(order_router)
api_router.include_router(product_router)
