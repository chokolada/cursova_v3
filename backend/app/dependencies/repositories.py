from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.room_repository import RoomRepository
from app.repositories.booking_repository import BookingRepository
from app.repositories.offer_repository import OfferRepository


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    """Dependency to get UserRepository."""
    return UserRepository(db)


def get_room_repository(db: AsyncSession = Depends(get_db)) -> RoomRepository:
    """Dependency to get RoomRepository."""
    return RoomRepository(db)


def get_booking_repository(db: AsyncSession = Depends(get_db)) -> BookingRepository:
    """Dependency to get BookingRepository."""
    return BookingRepository(db)


def get_offer_repository(db: AsyncSession = Depends(get_db)) -> OfferRepository:
    """Dependency to get OfferRepository."""
    return OfferRepository(db)
