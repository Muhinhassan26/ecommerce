from typing import Annotated

from fastapi import APIRouter, Depends, Request
from src.modules.users.schemas import ChangePassword, GetProfile, ResponseMessage, UpdateProfile
from src.modules.users.services.user import UserService

router = APIRouter(
    prefix="/users",
)


@router.get("/profile/", response_model=GetProfile)
async def get_profile(
    request: Request, user_service: Annotated[UserService, Depends(UserService)]
) -> GetProfile:
    user_id = request.state.user.get("user_id")
    return await user_service.get_profile(user_id=user_id)


@router.patch("/update-profile/", response_model=ResponseMessage)
async def update_profile(
    request: Request,
    update_profile: UpdateProfile,
    user_service: Annotated[UserService, Depends(UserService)],
) -> ResponseMessage:
    user_id = request.state.user.get("user_id")
    await user_service.update_profile(user_id=user_id, update_profile=update_profile)
    return ResponseMessage(message="Profile updated successfully")


@router.patch("/change-password/", response_model=ResponseMessage)
async def change_password(
    request: Request,
    new_password: ChangePassword,
    user_service: Annotated[UserService, Depends(UserService)],
) -> ResponseMessage:
    user_id = request.state.user.get("user_id")
    await user_service.update_password(user_id=user_id, new_password=new_password)
    return ResponseMessage(message="Password changed successfully")
