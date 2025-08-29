from enum import Enum


class UserRole(str, Enum):
    ORDER_MANAGER = "ORDER_MANAGER"
    PRODUCT_MANAGER = "PRODUCT_MANAGER"
    ADMIN = "ADMIN"
