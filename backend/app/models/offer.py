import enum
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Float, Enum as SQLEnum, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.room import Room
    from app.models.booking import Booking


class OfferType(str, enum.Enum):
    """Enum for offer types."""
    GLOBAL = "global"  # Available for all rooms
    ROOM_SPECIFIC = "room_specific"  # Only for specific room types


# Association table for room-offer many-to-many relationship
room_offers = Table(
    "room_offers",
    Base.metadata,
    Column("room_id", ForeignKey("rooms.id", ondelete="CASCADE"), primary_key=True),
    Column("offer_id", ForeignKey("offers.id", ondelete="CASCADE"), primary_key=True),
)


# Association table for booking-offer many-to-many relationship
booking_offers = Table(
    "booking_offers",
    Base.metadata,
    Column("booking_id", ForeignKey("bookings.id", ondelete="CASCADE"), primary_key=True),
    Column("offer_id", ForeignKey("offers.id", ondelete="CASCADE"), primary_key=True),
)


class Offer(Base):
    """Offer model representing special services and amenities."""

    __tablename__ = "offers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(500))
    price: Mapped[float] = mapped_column(Float)
    offer_type: Mapped[OfferType] = mapped_column(
        SQLEnum(OfferType, native_enum=False),
        default=OfferType.GLOBAL
    )
    is_active: Mapped[bool] = mapped_column(default=True)

    # Relationships
    rooms: Mapped[List["Room"]] = relationship(
        "Room",
        secondary=room_offers,
        back_populates="available_offers",
        lazy="noload"
    )
    bookings: Mapped[List["Booking"]] = relationship(
        "Booking",
        secondary=booking_offers,
        back_populates="selected_offers",
        lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<Offer {self.name} - ${self.price}>"
