from pydantic import BaseModel, EmailStr
from src.core.helpers import UserRole


class UpdateUser(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    username: str | None = None
    password: str | None = None
    is_active: str | None = None
    is_staff: str | None = None
    is_superadmin: str | None = None
    role: UserRole | None = None


class CreateAdmin(BaseModel):
    first_name: str
    last_name: str
    email: str
    username: str
    password: str
    is_active: bool = True
    is_staff: bool = False
    is_superadmin: bool = False
    role: UserRole = None


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    username: str
    is_active: bool
    is_staff: bool
    is_superadmin: bool
    role: str | None = None


class UpdateProfile(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    username: str | None = None


class GetProfile(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    username: str
    is_active: bool


class ChangePassword(BaseModel):
    new_password: str


class ResponseMessage(BaseModel):
    message: str
