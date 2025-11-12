from .admin import router as admin_product_router
from .user import router as user_product_router

__all__ = [
    "admin_product_router",
    "user_product_router",
]
