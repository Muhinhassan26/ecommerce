from fastapi import APIRouter
from src.modules.users.controllers import admin_router, user_router

api_router = APIRouter()

api_router.include_router(
    admin_router,
    prefix="/admin",
    tags=["User Admin"],
)


api_router.include_router(
    user_router,
    prefix="/users",
    tags=["User"],
)
