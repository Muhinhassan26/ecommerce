from pydantic import BaseModel, Field


class OrderProductCreate(BaseModel):
    product_id: int = Field(..., description="ID of the product")
    quantity: int = Field(1, ge=1, description="Quantity of the product")


class OrderProductResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float
    total_price: float
    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    items: list[OrderProductCreate]


class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: float
    status: str
    order_products: list[OrderProductResponse]

    model_config = {"from_attributes": True}
