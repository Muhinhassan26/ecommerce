from fastapi import APIRouter, Depends
from src.core.dependencies import JWTHandler
from src.modules.products.controllers import admin_product_router, user_product_router

api_router = APIRouter()

api_router.include_router(
    admin_product_router,
    prefix="/admin",
    tags=["Admin Product"],
    dependencies=[Depends(JWTHandler())],
)


api_router.include_router(
    user_product_router,
    prefix="/users",
    tags=["User Product"],
    dependencies=[Depends(JWTHandler())],
)
