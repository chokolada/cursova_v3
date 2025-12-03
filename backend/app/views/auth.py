from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from app.controllers.auth_controller import AuthController
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.schemas.auth import Token
from app.dependencies import get_user_repository
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Register a new user."""
    controller = AuthController(user_repo)
    user = await controller.register(user_data)
    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Login and get access token."""
    controller = AuthController(user_repo)
    login_data = UserLogin(username=form_data.username, password=form_data.password)
    return await controller.login(login_data)
