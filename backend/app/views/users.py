from typing import List
from fastapi import APIRouter, Depends, status
from app.controllers.user_controller import UserController
from app.schemas.user import UserResponse, UserUpdate
from app.dependencies import get_user_repository, get_current_user, require_manager
from app.repositories.user_repository import UserRepository
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


@router.get("/", response_model=List[UserResponse], dependencies=[Depends(require_manager)])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Get all users (manager only)."""
    controller = UserController(user_repo)
    return await controller.get_all_users(skip, limit)


@router.get("/{user_id}", response_model=UserResponse, dependencies=[Depends(require_manager)])
async def get_user(
    user_id: int,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Get user by ID (manager only)."""
    controller = UserController(user_repo)
    return await controller.get_user(user_id)


@router.put("/{user_id}", response_model=UserResponse, dependencies=[Depends(require_manager)])
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Update user (manager only)."""
    controller = UserController(user_repo)
    return await controller.update_user(user_id, user_data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_manager)])
async def delete_user(
    user_id: int,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Delete user (manager only)."""
    controller = UserController(user_repo)
    await controller.delete_user(user_id)
