from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db import get_db
from src.modules.users.models import User

from core.repository.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: Annotated[AsyncSession, Depends(get_db)]):
        super().__init__(model=User, session=session)
