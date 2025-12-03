import asyncio
import sys
from passlib.context import CryptContext
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.user import User, UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_admin_user():
    """Create the initial admin user."""
    async with AsyncSessionLocal() as session:
        # Check if user already exists
        result = await session.execute(
            select(User).where(User.username == "Maks")
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"User 'Maks' already exists with role: {existing_user.role}")
            return

        # Create admin user
        hashed_password = pwd_context.hash("Pass123!")

        admin_user = User(
            username="Maks",
            email="maksymbornak@gmail.com",
            hashed_password=hashed_password,
            full_name="Maks Bornak",
            role=UserRole.ADMIN,
            is_active=True
        )

        session.add(admin_user)
        await session.commit()
        await session.refresh(admin_user)

        print(f"✅ Admin user created successfully!")
        print(f"   Username: {admin_user.username}")
        print(f"   Email: {admin_user.email}")
        print(f"   Role: {admin_user.role}")
        print(f"   ID: {admin_user.id}")


if __name__ == "__main__":
    asyncio.run(create_admin_user())
