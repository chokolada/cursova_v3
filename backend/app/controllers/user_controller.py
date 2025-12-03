from typing import List, Optional
from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


class UserController:
    """Controller for user operations."""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_user(self, user_id: int) -> User:
        """Get user by ID."""
        user = await self.user_repo.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users."""
        return await self.user_repo.get_all(skip, limit)

    async def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all active users."""
        return await self.user_repo.get_active_users(skip, limit)

    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Update user."""
        user = await self.user_repo.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Update fields
        if user_data.email is not None:
            existing = await self.user_repo.get_by_email(user_data.email)
            if existing and existing.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            user.email = user_data.email

        if user_data.username is not None:
            existing = await self.user_repo.get_by_username(user_data.username)
            if existing and existing.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
            user.username = user_data.username

        if user_data.full_name is not None:
            user.full_name = user_data.full_name

        if user_data.password is not None:
            user.hashed_password = get_password_hash(user_data.password)

        if user_data.role is not None:
            user.role = user_data.role

        if user_data.is_active is not None:
            user.is_active = user_data.is_active

        return await self.user_repo.update(user)

    async def delete_user(self, user_id: int) -> None:
        """Delete user."""
        user = await self.user_repo.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        await self.user_repo.delete(user)
