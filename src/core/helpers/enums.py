from enum import Enum


class UserRole(str, Enum):
    ORDER_MANAGER = "order_manager"
    PRODUCT_MANAGER = "PRODUCT_MANAGER"
