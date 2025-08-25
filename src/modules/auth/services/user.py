from typing import Annotated

from fastapi import Depends
from src.core.error.exceptions import EmailAlreadyExistsError
from src.core.logger import logger
from src.modules.users.repository import UserRepository

from modules.auth.schemas import UserRegisterSchema


class UserAuthService:
    def __init__(self, user_repository: Annotated[UserRepository, Depends(UserRepository)]):
        self.user_repository = user_repository
        self.logger = logger

    async def register(self, user_data: UserRegisterSchema):
        user = await self.user_repository.get_by_filed(obj_in=user_data.email)

        if user:
            self.logger.warning(f"User with email {user_data.email} already exists.")
            raise EmailAlreadyExistsError()
