from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column
from src.core.models import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    first_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False)
    is_superadmin: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[str] = mapped_column(String(50), nullable=True)
