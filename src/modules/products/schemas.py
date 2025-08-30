from pydantic import BaseModel


class ProductBase(BaseModel):
    name: str
    description: str | None = None
    price: float
    stock: int = 0
    is_active: bool = True
    category: str | None = None

    class Config:  # noqa: D106
        orm_mode = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int
