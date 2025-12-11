from typing import List
from fastapi import APIRouter, Depends, status, Query
from app.controllers.room_controller import RoomController
from app.schemas.room import RoomCreate, RoomUpdate, RoomResponse
from app.dependencies import get_room_repository, require_manager
from app.repositories.room_repository import RoomRepository

router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.get("/", response_model=List[RoomResponse])
async def get_all_rooms(
    skip: int = 0,
    limit: int = 100,
    available_only: bool = Query(False),
    room_type: str = Query(None),
    min_price: float = Query(None),
    max_price: float = Query(None),
    capacity: int = Query(None),
    amenities: str = Query(None),
    room_repo: RoomRepository = Depends(get_room_repository)
):
    """Get all rooms with optional filters."""
    controller = RoomController(room_repo)
    return await controller.get_rooms_filtered(
        skip=skip,
        limit=limit,
        available_only=available_only,
        room_type=room_type,
        min_price=min_price,
        max_price=max_price,
        capacity=capacity,
        amenities=amenities
    )


@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(
    room_id: int,
    room_repo: RoomRepository = Depends(get_room_repository)
):
    """Get room by ID."""
    controller = RoomController(room_repo)
    return await controller.get_room(room_id)


@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_manager)])
async def create_room(
    room_data: RoomCreate,
    room_repo: RoomRepository = Depends(get_room_repository)
):
    """Create a new room (manager only)."""
    controller = RoomController(room_repo)
    return await controller.create_room(room_data)


@router.put("/{room_id}", response_model=RoomResponse, dependencies=[Depends(require_manager)])
async def update_room(
    room_id: int,
    room_data: RoomUpdate,
    room_repo: RoomRepository = Depends(get_room_repository)
):
    """Update room (manager only)."""
    controller = RoomController(room_repo)
    return await controller.update_room(room_id, room_data)


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_manager)])
async def delete_room(
    room_id: int,
    room_repo: RoomRepository = Depends(get_room_repository)
):
    """Delete room (manager only)."""
    controller = RoomController(room_repo)
    await controller.delete_room(room_id)
