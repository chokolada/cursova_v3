from typing import List
from fastapi import APIRouter, Depends, status
from app.controllers.booking_controller import BookingController
from app.schemas.booking import BookingCreate, BookingUpdate, BookingResponse
from app.dependencies import (
    get_booking_repository,
    get_room_repository,
    get_current_user,
    require_manager
)
from app.repositories.booking_repository import BookingRepository
from app.repositories.room_repository import RoomRepository
from app.models.user import User

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.get("/my", response_model=List[BookingResponse])
async def get_my_bookings(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    booking_repo: BookingRepository = Depends(get_booking_repository),
    room_repo: RoomRepository = Depends(get_room_repository)
):
    """Get current user's bookings."""
    controller = BookingController(booking_repo, room_repo)
    return await controller.get_user_bookings(current_user.id, skip, limit)


@router.get("/all", response_model=List[BookingResponse], dependencies=[Depends(require_manager)])
async def get_all_bookings(
    skip: int = 0,
    limit: int = 100,
    booking_repo: BookingRepository = Depends(get_booking_repository),
    room_repo: RoomRepository = Depends(get_room_repository)
):
    """Get all bookings (manager only)."""
    controller = BookingController(booking_repo, room_repo)
    return await controller.get_all_bookings(skip, limit)


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    booking_repo: BookingRepository = Depends(get_booking_repository),
    room_repo: RoomRepository = Depends(get_room_repository)
):
    """Get booking by ID."""
    controller = BookingController(booking_repo, room_repo)
    return await controller.get_booking(booking_id, current_user)


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_user),
    booking_repo: BookingRepository = Depends(get_booking_repository),
    room_repo: RoomRepository = Depends(get_room_repository)
):
    """Create a new booking."""
    controller = BookingController(booking_repo, room_repo)
    return await controller.create_booking(booking_data, current_user.id)


@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: int,
    booking_data: BookingUpdate,
    current_user: User = Depends(get_current_user),
    booking_repo: BookingRepository = Depends(get_booking_repository),
    room_repo: RoomRepository = Depends(get_room_repository)
):
    """Update booking."""
    controller = BookingController(booking_repo, room_repo)
    return await controller.update_booking(booking_id, booking_data, current_user)


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    booking_repo: BookingRepository = Depends(get_booking_repository),
    room_repo: RoomRepository = Depends(get_room_repository)
):
    """Cancel a booking."""
    controller = BookingController(booking_repo, room_repo)
    return await controller.cancel_booking(booking_id, current_user)


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_manager)])
async def delete_booking(
    booking_id: int,
    booking_repo: BookingRepository = Depends(get_booking_repository),
    room_repo: RoomRepository = Depends(get_room_repository)
):
    """Delete booking (manager only)."""
    controller = BookingController(booking_repo, room_repo)
    await controller.delete_booking(booking_id)
