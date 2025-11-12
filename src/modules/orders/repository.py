from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db import get_db
from src.core.repository.base import BaseRepository
from src.modules.orders.models import Order


class OrderRepository(BaseRepository[Order]):
    def __init__(self, session: Annotated[AsyncSession, Depends(get_db)]):
        super().__init__(model=Order, session=session)
