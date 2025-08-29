import asyncio

from sqlalchemy import select
from src.core.db.connection import async_session
from src.core.security import PasswordHandler
from src.modules.users.models import User


async def create_superadmin():
    async with async_session() as session:
        # check if superadmin already exists
        result = await session.execute(select(User).where(User.is_superadmin is True))
        admin = result.scalar_one_or_none()
        if admin:
            print("Superadmin already exists:", admin.username)
            return

        # create new superadmin
        superadmin = User(
            first_name="Super",
            last_name="Admin",
            email="superadmin@gmail.com",
            username="superadmin",
            password=PasswordHandler.hash("supersecurepassword"),
            is_active=True,
            is_staff=True,
            is_superadmin=True,
            role="admin",
        )
        session.add(superadmin)
        await session.commit()
        print("Superadmin created successfully!")


if __name__ == "__main__":
    asyncio.run(create_superadmin())
