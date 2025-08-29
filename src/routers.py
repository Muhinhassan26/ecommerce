from fastapi import APIRouter
from src.modules.auth.routers import api_router as auth_router
from src.modules.users.routers import api_router as user_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(user_router)
