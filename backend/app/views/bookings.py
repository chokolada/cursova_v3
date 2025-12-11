from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, status, Query, HTTPException
from app.controllers.booking_controller import BookingController
from app.schemas.booking import BookingCreate, BookingUpdate, BookingResponse, BookedDateRange, BookingExtend
from app.dependencies import (
    get_booking_repository,
    get_room_repository,
    get_offer_repository,
    get_current_user,
    require_manager
)
from app.repositories.booking_repository import BookingRepository
from app.repositories.room_repository import RoomRepository
from app.repositories.offer_repository import OfferRepository
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
    room_repo: RoomRepository = Depends(get_room_repository),
    offer_repo: OfferRepository = Depends(get_offer_repository)
):
    """Create a new booking."""
    controller = BookingController(booking_repo, room_repo, offer_repo)
    return await controller.create_booking(booking_data, current_user.id)


@router.get("/room/{room_id}/booked-dates", response_model=List[BookedDateRange])
async def get_room_booked_dates(
    room_id: int,
    start_date: datetime = Query(None, description="Start of window to check availability"),
    end_date: datetime = Query(None, description="End of window to check availability"),
    booking_repo: BookingRepository = Depends(get_booking_repository),
    room_repo: RoomRepository = Depends(get_room_repository)
):
    """Return booked date ranges for a room to disable dates in date pickers."""
    # Default window: from today for the next 12 months
    now = datetime.utcnow()
    start = start_date or now
    end = end_date or (start + timedelta(days=365))

    room = await room_repo.get(room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    controller = BookingController(booking_repo, room_repo)
    return await controller.get_room_booked_date_ranges(room_id, start, end)


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


@router.post("/{booking_id}/extend", response_model=BookingResponse)
async def extend_booking(
    booking_id: int,
    extend_data: BookingExtend,
    current_user: User = Depends(get_current_user),
    booking_repo: BookingRepository = Depends(get_booking_repository),
    room_repo: RoomRepository = Depends(get_room_repository)
):
    """Extend a booking by adding days to check-out date."""
    controller = BookingController(booking_repo, room_repo)
    return await controller.extend_booking(booking_id, extend_data.days, current_user)


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_manager)])
async def delete_booking(
    booking_id: int,
    booking_repo: BookingRepository = Depends(get_booking_repository),
    room_repo: RoomRepository = Depends(get_room_repository)
):
    """Delete booking (manager only)."""
    controller = BookingController(booking_repo, room_repo)
    await controller.delete_booking(booking_id)
