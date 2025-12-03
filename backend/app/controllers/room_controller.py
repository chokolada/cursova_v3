from typing import List
from fastapi import HTTPException, status
from app.repositories.room_repository import RoomRepository
from app.models.room import Room
from app.schemas.room import RoomCreate, RoomUpdate


class RoomController:
    """Controller for room operations."""

    def __init__(self, room_repo: RoomRepository):
        self.room_repo = room_repo

    async def get_room(self, room_id: int) -> Room:
        """Get room by ID."""
        room = await self.room_repo.get(room_id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found"
            )
        return room

    async def get_all_rooms(self, skip: int = 0, limit: int = 100) -> List[Room]:
        """Get all rooms."""
        return await self.room_repo.get_all(skip, limit)

    async def get_available_rooms(self, skip: int = 0, limit: int = 100) -> List[Room]:
        """Get all available rooms."""
        return await self.room_repo.get_available_rooms(skip, limit)

    async def get_rooms_by_type(self, room_type: str, skip: int = 0, limit: int = 100) -> List[Room]:
        """Get rooms by type."""
        return await self.room_repo.get_by_room_type(room_type, skip, limit)

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
        """Get rooms with multiple filters applied."""
        return await self.room_repo.get_rooms_filtered(
            skip=skip,
            limit=limit,
            available_only=available_only,
            room_type=room_type,
            min_price=min_price,
            max_price=max_price,
            capacity=capacity
        )

    async def create_room(self, room_data: RoomCreate) -> Room:
        """Create a new room."""
        # Check if room number already exists
        existing = await self.room_repo.get_by_room_number(room_data.room_number)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Room number already exists"
            )

        room = Room(**room_data.model_dump())
        return await self.room_repo.create(room)

    async def update_room(self, room_id: int, room_data: RoomUpdate) -> Room:
        """Update room."""
        room = await self.room_repo.get(room_id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found"
            )

        # Update fields
        update_data = room_data.model_dump(exclude_unset=True)

        if "room_number" in update_data:
            existing = await self.room_repo.get_by_room_number(update_data["room_number"])
            if existing and existing.id != room_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Room number already exists"
                )

        for field, value in update_data.items():
            setattr(room, field, value)

        return await self.room_repo.update(room)

    async def delete_room(self, room_id: int) -> None:
        """Delete room."""
        room = await self.room_repo.get(room_id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found"
            )
        await self.room_repo.delete(room)
