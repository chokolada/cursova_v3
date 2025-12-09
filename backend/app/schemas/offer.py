from pydantic import BaseModel, Field
from typing import Optional
from app.models.offer import OfferType


class OfferBase(BaseModel):
    """Base schema for Offer."""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    price: float = Field(..., ge=0)
    offer_type: OfferType = OfferType.GLOBAL
    is_active: bool = True


class OfferCreate(OfferBase):
    """Schema for creating an offer."""
    pass


class OfferUpdate(BaseModel):
    """Schema for updating an offer."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    price: Optional[float] = Field(None, ge=0)
    offer_type: Optional[OfferType] = None
    is_active: Optional[bool] = None


class OfferResponse(OfferBase):
    """Schema for offer response."""
    id: int

    class Config:
        from_attributes = True
