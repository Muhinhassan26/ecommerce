from typing import Annotated

from fastapi import APIRouter, Depends
from src.core.dependencies.query_params import CommonQueryParam
from src.core.schemas.common import PaginatedResponse, QueryParams
from src.modules.users.schemas import CreateAdmin, ResponseMessage, UpdateUser, UserResponse
from src.modules.users.services import AdminService

router = APIRouter(prefix="/admin")


@router.get("/users", response_model=list[UserResponse])
async def get_users(
    admin_service: Annotated[AdminService, Depends(AdminService)],
) -> list[UserResponse]:
    return await admin_service.get_all_users()


@router.get("/users/paginate", response_model=PaginatedResponse[UserResponse])
async def get_users(  # noqa: F811
    admin_service: Annotated[AdminService, Depends(AdminService)],
    query_params: QueryParams = Depends(CommonQueryParam(filter_fields=["username", "email"])),
) -> PaginatedResponse[UserResponse]:
    return await admin_service.get_paginate_users(query_params=query_params)


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    admin_service: Annotated[AdminService, Depends(AdminService)],
) -> UserResponse:
    return await admin_service.get_user_by_id(user_id=user_id)


@router.patch("/users/{user_id}", response_model=ResponseMessage)
async def update_user(
    user_id: int,
    update_user: UpdateUser,
    admin_service: Annotated[AdminService, Depends(AdminService)],
) -> ResponseMessage:
    await admin_service.update_user(user_id=user_id, update_user=update_user)
    return ResponseMessage(message="User updated successfully")


@router.post("create-admin", response_model=ResponseMessage)
async def create_admin(
    create_admin: CreateAdmin, admin_service: Annotated[AdminService, Depends(AdminService)]
) -> ResponseMessage:
    return await admin_service._create_admin(create_admin=create_admin)
