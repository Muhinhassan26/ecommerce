from pydantic import BaseModel


class ProductBase(BaseModel):
    model_config = {"from_attributes": True}
    name: str
    description: str | None = None
    price: float
    stock: int = 0
    is_active: bool = True
    category: str | None = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int
