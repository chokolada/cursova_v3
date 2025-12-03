from typing import List
from datetime import datetime
from fastapi import HTTPException, status
from app.repositories.booking_repository import BookingRepository
from app.repositories.room_repository import RoomRepository
from app.models.booking import Booking, BookingStatus
from app.models.user import User, UserRole
from app.schemas.booking import BookingCreate, BookingUpdate


class BookingController:
    """Controller for booking operations."""

    def __init__(self, booking_repo: BookingRepository, room_repo: RoomRepository):
        self.booking_repo = booking_repo
        self.room_repo = room_repo

    async def get_booking(self, booking_id: int, current_user: User) -> Booking:
        """Get booking by ID."""
        booking = await self.booking_repo.get_with_relations(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )

        # Users can only see their own bookings, managers can see all
        if current_user.role == UserRole.USER and booking.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this booking"
            )

        return booking

    async def get_all_bookings(self, skip: int = 0, limit: int = 100) -> List[Booking]:
        """Get all bookings (manager only)."""
        return await self.booking_repo.get_all(skip, limit)

    async def get_user_bookings(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Booking]:
        """Get bookings for a specific user."""
        return await self.booking_repo.get_user_bookings(user_id, skip, limit)

    async def create_booking(self, booking_data: BookingCreate, user_id: int) -> Booking:
        """Create a new booking."""
        # Check if room exists and is available
        room = await self.room_repo.get(booking_data.room_id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found"
            )

        if not room.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Room is not available"
            )

        # Check capacity
        if booking_data.guests_count > room.capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Room capacity is {room.capacity} guests"
            )

        # Calculate total price
        days = (booking_data.check_out_date - booking_data.check_in_date).days
        if days <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Check-out date must be after check-in date"
            )

        total_price = days * room.price_per_night

        # Create booking
        booking = Booking(
            user_id=user_id,
            room_id=booking_data.room_id,
            check_in_date=booking_data.check_in_date,
            check_out_date=booking_data.check_out_date,
            guests_count=booking_data.guests_count,
            total_price=total_price,
            special_requests=booking_data.special_requests,
            status=BookingStatus.PENDING,
        )

        return await self.booking_repo.create(booking)

    async def update_booking(
        self, booking_id: int, booking_data: BookingUpdate, current_user: User
    ) -> Booking:
        """Update booking."""
        booking = await self.booking_repo.get(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )

        # Users can only update their own bookings
        if current_user.role == UserRole.USER and booking.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this booking"
            )

        # Update fields
        update_data = booking_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(booking, field, value)

        # Recalculate price if dates changed
        if "check_in_date" in update_data or "check_out_date" in update_data:
            room = await self.room_repo.get(booking.room_id)
            days = (booking.check_out_date - booking.check_in_date).days
            booking.total_price = days * room.price_per_night

        return await self.booking_repo.update(booking)

    async def cancel_booking(self, booking_id: int, current_user: User) -> Booking:
        """Cancel a booking."""
        booking = await self.booking_repo.get(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )

        # Users can only cancel their own bookings
        if current_user.role == UserRole.USER and booking.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to cancel this booking"
            )

        booking.status = BookingStatus.CANCELLED
        return await self.booking_repo.update(booking)

    async def delete_booking(self, booking_id: int) -> None:
        """Delete booking (manager only)."""
        booking = await self.booking_repo.get(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        await self.booking_repo.delete(booking)
