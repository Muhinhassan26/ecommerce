from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db import get_db
from src.core.repository.base import BaseRepository
from src.modules.products.models import Product


class ProductRepository(BaseRepository[Product]):
    def __init__(self, session: Annotated[AsyncSession, Depends(get_db)]):
        super().__init__(model=Product, session=session)
