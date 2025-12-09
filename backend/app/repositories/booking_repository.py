from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.booking import Booking, BookingStatus
from app.repositories.base import BaseRepository


class BookingRepository(BaseRepository[Booking]):
    """Repository for Booking model."""

    def __init__(self, db: AsyncSession):
        super().__init__(Booking, db)

    async def create(self, booking: Booking) -> Booking:
        """Create a new booking and reload with relationships."""
        self.db.add(booking)
        await self.db.flush()
        await self.db.refresh(booking)

        # Reload the booking with all relationships
        result = await self.db.execute(
            select(Booking)
            .options(
                selectinload(Booking.user),
                selectinload(Booking.room),
                selectinload(Booking.selected_offers)
            )
            .where(Booking.id == booking.id)
        )
        return result.scalar_one()

    async def update(self, booking: Booking) -> Booking:
        """Update booking and reload with relationships."""
        await self.db.flush()
        await self.db.refresh(booking)

        # Reload the booking with all relationships
        result = await self.db.execute(
            select(Booking)
            .options(
                selectinload(Booking.user),
                selectinload(Booking.room),
                selectinload(Booking.selected_offers)
            )
            .where(Booking.id == booking.id)
        )
        return result.scalar_one()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Booking]:
        """Get all bookings with relations."""
        result = await self.db.execute(
            select(Booking)
            .options(
                selectinload(Booking.user),
                selectinload(Booking.room),
                selectinload(Booking.selected_offers)
            )
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_with_relations(self, id: int):
        """Get booking with user and room relations."""
        result = await self.db.execute(
            select(Booking)
            .options(
                selectinload(Booking.user),
                selectinload(Booking.room),
                selectinload(Booking.selected_offers)
            )
            .where(Booking.id == id)
        )
        return result.scalar_one_or_none()

    async def get_user_bookings(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Booking]:
        """Get all bookings for a specific user."""
        result = await self.db.execute(
            select(Booking)
            .options(
                selectinload(Booking.room),
                selectinload(Booking.selected_offers)
            )
            .where(Booking.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_room_bookings(self, room_id: int, skip: int = 0, limit: int = 100) -> List[Booking]:
        """Get all bookings for a specific room."""
        result = await self.db.execute(
            select(Booking)
            .options(
                selectinload(Booking.user),
                selectinload(Booking.selected_offers)
            )
            .where(Booking.room_id == room_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_status(self, status: BookingStatus, skip: int = 0, limit: int = 100) -> List[Booking]:
        """Get bookings by status."""
        result = await self.db.execute(
            select(Booking)
            .options(
                selectinload(Booking.user),
                selectinload(Booking.room),
                selectinload(Booking.selected_offers)
            )
            .where(Booking.status == status)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
