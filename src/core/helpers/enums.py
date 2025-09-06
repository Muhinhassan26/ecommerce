from enum import Enum


class UserRole(str, Enum):
    ORDER_MANAGER = "ORDER_MANAGER"
    PRODUCT_MANAGER = "PRODUCT_MANAGER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    CANCELLED = "CANCELLED"
