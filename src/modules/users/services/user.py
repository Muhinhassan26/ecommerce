from typing import Annotated

from fastapi import Depends
from src.core.error.codes import INVALID_CRED, NO_DATA
from src.core.error.exceptions import InvalidCredentialsException, NotFoundException
from src.core.error.format_error import ERROR_MAPPER
from src.core.logger import logger
from src.core.security import PasswordHandler
from src.modules.users.models import User
from src.modules.users.repository import UserRepository
from src.modules.users.schemas import ChangePassword, UpdateProfile


class UserService:
    def __init__(self, user_repository: Annotated[UserRepository, Depends(UserRepository)]):
        self.user_repository = user_repository
        self.logger = logger

    async def get_profile(self, user_id: int) -> User:
        user = await self.user_repository.get_by_id(obj_id=user_id)

        if not user:
            raise NotFoundException(message=ERROR_MAPPER[NO_DATA])
        return user

    async def update_profile(self, user_id: int, update_profile: UpdateProfile) -> User:
        filters = {"id": user_id}
        updated_user = await self.user_repository.update_obj(
            where=filters,
            values=update_profile.model_dump(
                exclude_none=True,
            ),
        )
        if updated_user == 0:
            logger.warning(f"User profile update failed:  user_id={user_id}")
            raise NotFoundException(message=ERROR_MAPPER[NO_DATA])
        self.logger.info(f"User profile updated successfully: user_id={user_id}")
        return updated_user

    async def update_password(self, user_id: int, new_password: ChangePassword) -> User:
        user = self.user_repository.get_by_id(obj_id=user_id)

        if not user:
            raise NotFoundException(message=ERROR_MAPPER[NO_DATA])

        if not PasswordHandler.verify_password(new_password.new_password, user.password):
            raise InvalidCredentialsException(message=ERROR_MAPPER[INVALID_CRED])

        new_hashed_passowrd = PasswordHandler.hash(new_password.new_password)
        filters = {"id": user_id}

        updated_user = await self.user_repository.update_obj(
            where=filters, values={"password": new_hashed_passowrd}
        )
        if updated_user == 0:
            logger.warning(f"User password update failed:  user_id={user_id}")
            raise NotFoundException(message=ERROR_MAPPER[NO_DATA])
        self.logger.info(f"User password updated successfully: user_id={user_id}")
        return updated_user
