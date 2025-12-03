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

    async def get_with_relations(self, id: int):
        """Get booking with user and room relations."""
        result = await self.db.execute(
            select(Booking)
            .options(selectinload(Booking.user), selectinload(Booking.room))
            .where(Booking.id == id)
        )
        return result.scalar_one_or_none()

    async def get_user_bookings(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Booking]:
        """Get all bookings for a specific user."""
        result = await self.db.execute(
            select(Booking)
            .options(selectinload(Booking.room))
            .where(Booking.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_room_bookings(self, room_id: int, skip: int = 0, limit: int = 100) -> List[Booking]:
        """Get all bookings for a specific room."""
        result = await self.db.execute(
            select(Booking)
            .options(selectinload(Booking.user))
            .where(Booking.room_id == room_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_status(self, status: BookingStatus, skip: int = 0, limit: int = 100) -> List[Booking]:
        """Get bookings by status."""
        result = await self.db.execute(
            select(Booking)
            .options(selectinload(Booking.user), selectinload(Booking.room))
            .where(Booking.status == status)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
