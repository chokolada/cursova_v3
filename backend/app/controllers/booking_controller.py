from typing import List
from datetime import datetime
from fastapi import HTTPException, status
from app.repositories.booking_repository import BookingRepository
from app.repositories.room_repository import RoomRepository
from app.repositories.offer_repository import OfferRepository
from app.models.booking import Booking, BookingStatus
from app.models.user import User, UserRole
from app.schemas.booking import BookingCreate, BookingUpdate


class BookingController:
    """Controller for booking operations."""

    def __init__(self, booking_repo: BookingRepository, room_repo: RoomRepository, offer_repo: OfferRepository = None):
        self.booking_repo = booking_repo
        self.room_repo = room_repo
        self.offer_repo = offer_repo

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

        # Prevent double-booking: check for overlapping bookings on this room
        overlapping = await self.booking_repo.get_overlapping_bookings(
            room_id=booking_data.room_id,
            start_date=booking_data.check_in_date,
            end_date=booking_data.check_out_date
        )
        if overlapping:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Room is already booked for the selected dates"
            )

        # Calculate total price
        days = (booking_data.check_out_date - booking_data.check_in_date).days
        if days <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Check-out date must be after check-in date"
            )

        total_price = days * room.price_per_night

        # Handle offers if any selected
        selected_offers = []
        if booking_data.offer_ids and self.offer_repo:
            # Fetch room with available offers
            from sqlalchemy import select
            from sqlalchemy.orm import selectinload
            from app.models.room import Room
            from app.database import AsyncSessionLocal

            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(Room).where(Room.id == room.id).options(selectinload(Room.available_offers))
                )
                room_with_offers = result.scalar_one_or_none()
                available_offer_ids = [o.id for o in room_with_offers.available_offers]

            # Validate and fetch selected offers
            for offer_id in booking_data.offer_ids:
                if offer_id not in available_offer_ids:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Offer {offer_id} is not available for this room"
                    )
                offer = await self.offer_repo.get(offer_id)
                if not offer or not offer.is_active:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Offer {offer_id} is not available"
                    )
                selected_offers.append(offer)
                total_price += offer.price

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

        # Assign offers to booking
        if selected_offers:
            booking.selected_offers = selected_offers

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
            # Use updated values if provided, otherwise existing ones
            new_check_in = update_data.get("check_in_date", booking.check_in_date)
            new_check_out = update_data.get("check_out_date", booking.check_out_date)

            # Prevent overlaps with other bookings
            overlapping = await self.booking_repo.get_overlapping_bookings(
                room_id=booking.room_id,
                start_date=new_check_in,
                end_date=new_check_out,
                exclude_booking_id=booking.id
            )
            if overlapping:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Room is already booked for the selected dates"
                )

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

    async def extend_booking(self, booking_id: int, days: int, current_user: User) -> Booking:
        """Extend a booking by adding days to check-out date."""
        from datetime import timedelta

        booking = await self.booking_repo.get(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )

        # Users can only extend their own bookings
        if current_user.role == UserRole.USER and booking.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to extend this booking"
            )

        # Can only extend pending or confirmed bookings
        if booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only extend pending or confirmed bookings"
            )

        # Validate days
        if days <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Days must be a positive number"
            )

        # Calculate new check-out date
        new_check_out = booking.check_out_date + timedelta(days=days)

        # Check for overlapping bookings with extended dates
        overlapping = await self.booking_repo.get_overlapping_bookings(
            room_id=booking.room_id,
            start_date=booking.check_in_date,
            end_date=new_check_out,
            exclude_booking_id=booking.id
        )
        if overlapping:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot extend: room is already booked for the extended dates"
            )

        # Update check-out date
        booking.check_out_date = new_check_out

        # Recalculate total price
        room = await self.room_repo.get(booking.room_id)
        duration = (booking.check_out_date - booking.check_in_date).days
        booking.total_price = room.price_per_night * duration

        # Add offer prices if any
        if booking.selected_offers:
            for offer in booking.selected_offers:
                booking.total_price += offer.price

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

    async def get_room_booked_date_ranges(
        self,
        room_id: int,
        start_date: datetime,
        end_date: datetime
    ):
        """Return booked date ranges for a room (for availability/date pickers)."""
        return await self.booking_repo.get_booked_ranges(
            room_id=room_id,
            start_date=start_date,
            end_date=end_date
        )
