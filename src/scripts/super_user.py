import asyncio

from sqlalchemy import select
from src.core.db.connection import async_session
from src.core.helpers.enums import UserRole
from src.core.security import PasswordHandler
from src.modules.orders.models import Order, OrderProduct  # noqa
from src.modules.products.models import Product  # noqa
from src.modules.users.models import User


async def create_superadmin() -> None:
    async with async_session() as session:
        # check if superadmin already exists
        result = await session.execute(select(User).where(User.is_superadmin == True))  # noqa: E712
        admin = result.scalar_one_or_none()
        if admin:
            print("Superadmin already exists:", admin.username)
            return
        first_name = input("Enter first name: ")
        last_name = input("Enter last name: ")
        email = input("Enter email: ")
        username = input("Enter username: ")
        password = input("Enter password: ")

        # create new superadmin
        superadmin = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            password=PasswordHandler.hash(password=password),
            is_active=True,
            is_staff=True,
            is_superadmin=True,
            role=UserRole.SUPER_ADMIN.value,
        )
        session.add(superadmin)
        await session.commit()
        print("Superadmin created successfully!")


if __name__ == "__main__":
    asyncio.run(create_superadmin())
