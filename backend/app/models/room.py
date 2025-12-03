from sqlalchemy import String, Integer, Float, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from app.database import Base


class Room(Base):
    """Room model."""

    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    room_number: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)
    room_type: Mapped[str] = mapped_column(String(50), nullable=False)  # single, double, suite, etc.
    price_per_night: Mapped[float] = mapped_column(Float, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)  # number of guests
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    amenities: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string or comma-separated
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    floor: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    bookings: Mapped[List["Booking"]] = relationship(
        "Booking", back_populates="room", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Room {self.room_number} ({self.room_type})>"
