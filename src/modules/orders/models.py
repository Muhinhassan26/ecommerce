from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.models import BaseModel


class Order(BaseModel):
    __tablename__ = "orders"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.00)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")

    user = relationship("User", back_populates="orders")
    order_products = relationship("OrderProduct", back_populates="order")


class OrderProduct(BaseModel):
    __tablename__ = "order_products"

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    total_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="order_products")
    product = relationship("Product", back_populates="order_products")


# payloadd

# [

#     {
#         "product_id": 1,
#         "quantity": 2
#     },
#     {
#         "product_id": 2,
#         "quantity": 1
#     }
# ]
