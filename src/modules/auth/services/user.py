from typing import Annotated

from fastapi import Depends
from src.core.error.exceptions import (
    EmailAlreadyExistsException,
    InternalServerException,
    InvalidCredentialsException,
    NotFoundException,
)
from src.core.logger import logger
from src.core.schemas.common import FilterOptions
from src.core.security import PasswordHandler
from src.core.security.jwt_handler import JWTHandler
from src.modules.auth.schemas import (
    AccessTokenPayload,
    RefreshTokenPayload,
    TokenResponse,
    UserLoginSchema,
    UserRegisterSchema,
)
from src.modules.users.models import User
from src.modules.users.repository import UserRepository


class UserAuthService:
    def __init__(self, user_repository: Annotated[UserRepository, Depends(UserRepository)]):
        self.user_repository = user_repository
        self.logger = logger

    async def register(self, user_data: UserRegisterSchema) -> TokenResponse:
        filter_options = FilterOptions(
            filters={"email": user_data.email},
        )
        user = await self.user_repository.get_by_filed(filter_options=filter_options)

        if user:
            self.logger.warning(f"User with email {user_data.email} already exists.")
            raise EmailAlreadyExistsException()
        hashed_password = PasswordHandler.hash(user_data.password)

        user = User(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            username=user_data.username,
            password=hashed_password,
        )

        try:
            created_user = await self.user_repository.create(obj=user)

        except Exception as e:
            self.logger.error(f"Database error during user creation: {str(e)}")
            raise InternalServerException(errors=str(e)) from e

        self.logger.info(
            f"User registered successfully: user_id={created_user.id}, email={created_user.email}"
        )
        return self.generate_token(user_id=str(created_user.id))

    def generate_token(self, user_id: str) -> TokenResponse:
        access_payload = AccessTokenPayload(user_id=user_id, sub="access")
        refresh_payload = RefreshTokenPayload(user_id=user_id, sub="refresh")

        try:
            access_token, access_expire = JWTHandler.encode(
                token_type="access", payload=access_payload
            )
            refresh_token, _ = JWTHandler.encode(token_type="refresh", payload=refresh_payload)
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                user_id=user_id,
                access_token_expire=access_expire,
            )
        except Exception as e:
            self.logger.error(f"Token generation failed: {str(e)}")
            raise InternalServerException(errors="Token generation failed") from e

    async def login_user(self, login_data: UserLoginSchema) -> TokenResponse:
        filter_options = FilterOptions(
            filters={"email": login_data.username},
        )
        user = await self.user_repository.get_by_filed(filter_options=filter_options)
        if not user:
            self.logger.warning(f"User with username {login_data.username} not found.")
            raise NotFoundException()

        is_password_valid = PasswordHandler.verify_password(login_data.password, user.password)
        if not is_password_valid:
            self.logger.warning(f"Invalid password for username {login_data.username}.")
            raise InvalidCredentialsException()

        return self.generate_token(user_id=str(user.id))
