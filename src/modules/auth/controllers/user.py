from typing import Annotated

from fastapi import APIRouter, Depends, status
from src.core.logger import logger
from src.modules.auth.schemas import TokenResponse, UserLoginSchema, UserRegisterSchema
from src.modules.auth.services.user import UserAuthService

router = APIRouter(prefix="/user")


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserRegisterSchema,
    user_auth_service: Annotated[UserAuthService, Depends(UserAuthService)],
) -> TokenResponse:
    return await user_auth_service.register(user_data=user_data)


@router.post("/login/", response_model=TokenResponse)
async def process_login(
    user_auth_service: Annotated[UserAuthService, Depends(UserAuthService)],
    login_data: UserLoginSchema,
) -> TokenResponse:
    tokens = await user_auth_service.login_user(login_data=login_data)
    logger.info(f"Login successful for user_id={tokens.user_id}")
    return tokens
