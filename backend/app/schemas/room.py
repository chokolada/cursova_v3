from pydantic import BaseModel, Field
from typing import Optional


class RoomBase(BaseModel):
    """Base room schema."""
    room_number: str = Field(..., max_length=10)
    room_type: str = Field(..., max_length=50)
    price_per_night: float = Field(..., gt=0)
    capacity: int = Field(..., gt=0)
    description: Optional[str] = None
    amenities: Optional[str] = None
    floor: Optional[int] = None
    image_url: Optional[str] = None


class RoomCreate(RoomBase):
    """Schema for creating a room."""
    is_available: bool = True


class RoomUpdate(BaseModel):
    """Schema for updating a room."""
    room_number: Optional[str] = Field(None, max_length=10)
    room_type: Optional[str] = Field(None, max_length=50)
    price_per_night: Optional[float] = Field(None, gt=0)
    capacity: Optional[int] = Field(None, gt=0)
    description: Optional[str] = None
    amenities: Optional[str] = None
    is_available: Optional[bool] = None
    floor: Optional[int] = None
    image_url: Optional[str] = None


class RoomResponse(RoomBase):
    """Schema for room response."""
    id: int
    is_available: bool

    class Config:
        from_attributes = True
