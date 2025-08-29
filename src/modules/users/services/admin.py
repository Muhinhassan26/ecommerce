from typing import Annotated

from fastapi import Depends
from src.core.error.codes import NO_DATA
from src.core.error.exceptions import NotFoundException
from src.core.error.format_error import ERROR_MAPPER
from src.core.logger import logger
from src.core.schemas.common import FilterOptions, PaginatedResponse, QueryParams
from src.core.security import PasswordHandler
from src.core.service import BaseService
from src.modules.users.models import User
from src.modules.users.repository import UserRepository
from src.modules.users.schemas import CreateAdmin, ResponseMessage, UpdateUser, UserResponse


class AdminService(BaseService):
    def __init__(self, user_repository: Annotated[UserRepository, Depends(UserRepository)]):
        self.user_repository = user_repository
        self.logger = logger

    async def get_all_users(self) -> list[User]:
        filter_options = FilterOptions(sorting={"created_at": "desc"})
        return await self.user_repository.list_all(filter_options=filter_options)

    async def get_paginate_users(
        self,
        query_params: QueryParams,
    ) -> PaginatedResponse[UserResponse]:
        filter_options = FilterOptions(
            pagination=query_params,
            sorting={"created_at": "desc"},
            search_fields=["username", "email"],
        )
        users, total = await self.user_repository.paginate_filters(filter_options=filter_options)

        if not users:
            raise NotFoundException(message=ERROR_MAPPER[NO_DATA])

        return PaginatedResponse(
            data=users,
            meta=await self.setup_pagination_meta(
                total=total,
                page_size=query_params.page_size,
                page=query_params.page,
            ),
        )

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.user_repository.get_by_id(obj_id=user_id)

    async def update_user(self, user_id: int, update_user: UpdateUser):
        filters = {"id": user_id}
        updated_user = await self.user_repository.update_obj(
            where=filters,
            values=update_user.model_dump(
                exclude_none=True,
            ),
        )
        if updated_user == 0:
            logger.warning(f"User update failed:  user_id={user_id}")
            raise NotFoundException(message=ERROR_MAPPER[NO_DATA])

        logger.info(f"User updated:  user_id={user_id}")

    async def _create_admin(self, create_admin: CreateAdmin) -> ResponseMessage:
        admin = await self.user_repository.create(
            obj=User(
                **create_admin.model_dump(exclude={"password"}),
                password=PasswordHandler.hash(create_admin.password),
            )
        )
        logger.info(f"Admin created:  user_id={admin.id}")
        return ResponseMessage(message="Admin created successfully")
