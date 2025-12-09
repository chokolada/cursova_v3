from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from app.models.booking import BookingStatus
from app.schemas.offer import OfferResponse


class BookingBase(BaseModel):
    """Base booking schema."""
    room_id: int
    check_in_date: datetime
    check_out_date: datetime
    guests_count: int = Field(..., gt=0)
    special_requests: Optional[str] = None

    @field_validator('check_out_date')
    @classmethod
    def check_dates(cls, check_out_date: datetime, info) -> datetime:
        check_in_date = info.data.get('check_in_date')
        if check_in_date and check_out_date <= check_in_date:
            raise ValueError('check_out_date must be after check_in_date')
        return check_out_date


class BookingCreate(BookingBase):
    """Schema for creating a booking."""
    offer_ids: List[int] = Field(default_factory=list, description="List of offer IDs to include in booking")


class BookingUpdate(BaseModel):
    """Schema for updating a booking."""
    check_in_date: Optional[datetime] = None
    check_out_date: Optional[datetime] = None
    guests_count: Optional[int] = Field(None, gt=0)
    status: Optional[BookingStatus] = None
    special_requests: Optional[str] = None
    offer_ids: Optional[List[int]] = None


class BookingResponse(BookingBase):
    """Schema for booking response."""
    id: int
    user_id: int
    total_price: float
    status: BookingStatus
    created_at: datetime
    updated_at: datetime
    selected_offers: List[OfferResponse] = []

    class Config:
        from_attributes = True
