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


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    stock: int | None = None
    is_active: bool | None = None
    category: str | None = None


class ProductResponse(ProductBase):
    id: int


class ResponseMessage(BaseModel):
    message: str
