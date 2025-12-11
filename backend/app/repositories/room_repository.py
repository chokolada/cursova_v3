from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.room import Room
from app.repositories.base import BaseRepository


class RoomRepository(BaseRepository[Room]):
    """Repository for Room model."""

    def __init__(self, db: AsyncSession):
        super().__init__(Room, db)

    async def get(self, id: int) -> Optional[Room]:
        """Get a single room by ID with available offers."""
        result = await self.db.execute(
            select(Room)
            .options(selectinload(Room.available_offers))
            .where(Room.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Room]:
        """Get all rooms with available offers."""
        result = await self.db.execute(
            select(Room)
            .options(selectinload(Room.available_offers))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_room_number(self, room_number: str) -> Optional[Room]:
        """Get room by room number."""
        result = await self.db.execute(
            select(Room)
            .options(selectinload(Room.available_offers))
            .where(Room.room_number == room_number)
        )
        return result.scalar_one_or_none()

    async def get_available_rooms(self, skip: int = 0, limit: int = 100) -> List[Room]:
        """Get all available rooms."""
        result = await self.db.execute(
            select(Room)
            .options(selectinload(Room.available_offers))
            .where(Room.is_available == True)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_room_type(self, room_type: str, skip: int = 0, limit: int = 100) -> List[Room]:
        """Get rooms by type."""
        result = await self.db.execute(
            select(Room)
            .options(selectinload(Room.available_offers))
            .where(Room.room_type == room_type)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_rooms_filtered(
        self,
        skip: int = 0,
        limit: int = 100,
        available_only: bool = False,
        room_type: str = None,
        min_price: float = None,
        max_price: float = None,
        capacity: int = None
    ) -> List[Room]:
        """Get rooms with multiple filters."""
        query = select(Room).options(selectinload(Room.available_offers))

        # Apply filters
        if available_only:
            query = query.where(Room.is_available == True)

        if room_type:
            query = query.where(Room.room_type == room_type)

        if min_price is not None:
            query = query.where(Room.price_per_night >= min_price)

        if max_price is not None:
            query = query.where(Room.price_per_night <= max_price)

        if capacity is not None:
            query = query.where(Room.capacity >= capacity)

        # Apply pagination
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, room: Room) -> Room:
        """Create a new room and eagerly load offers to avoid async lazy-loading errors."""
        self.db.add(room)
        await self.db.flush()
        # Reload with offers eager-loaded so Pydantic serialization won't trigger lazy loads
        result = await self.db.execute(
            select(Room)
            .options(selectinload(Room.available_offers))
            .where(Room.id == room.id)
        )
        return result.scalar_one()

    async def update(self, room: Room) -> Room:
        """Update a room and return with offers eager-loaded."""
        await self.db.flush()
        result = await self.db.execute(
            select(Room)
            .options(selectinload(Room.available_offers))
            .where(Room.id == room.id)
        )
        return result.scalar_one()
