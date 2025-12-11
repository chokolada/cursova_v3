from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.repositories.factory import RepositoryFactory
from app.repositories.user_repository import UserRepository
from app.repositories.room_repository import RoomRepository
from app.repositories.booking_repository import BookingRepository
from app.repositories.offer_repository import OfferRepository


def _factory(db: AsyncSession) -> RepositoryFactory:
    """Helper to build a repository factory for the current DB session."""
    return RepositoryFactory(db)


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    """Dependency that uses Factory Method to provide UserRepository."""
    return _factory(db).create_user_repository()


def get_room_repository(db: AsyncSession = Depends(get_db)) -> RoomRepository:
    """Dependency that uses Factory Method to provide RoomRepository."""
    return _factory(db).create_room_repository()


def get_booking_repository(db: AsyncSession = Depends(get_db)) -> BookingRepository:
    """Dependency that uses Factory Method to provide BookingRepository."""
    return _factory(db).create_booking_repository()


def get_offer_repository(db: AsyncSession = Depends(get_db)) -> OfferRepository:
    """Dependency that uses Factory Method to provide OfferRepository."""
    return _factory(db).create_offer_repository()
