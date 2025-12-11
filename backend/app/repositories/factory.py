from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.repositories.room_repository import RoomRepository
from app.repositories.booking_repository import BookingRepository
from app.repositories.offer_repository import OfferRepository


class RepositoryFactory:
    """Factory Method for creating repositories bound to a DB session."""

    def __init__(self, db: AsyncSession):
        self._db = db

    def create_user_repository(self) -> UserRepository:
        """Create a UserRepository instance."""
        return UserRepository(self._db)

    def create_room_repository(self) -> RoomRepository:
        """Create a RoomRepository instance."""
        return RoomRepository(self._db)

    def create_booking_repository(self) -> BookingRepository:
        """Create a BookingRepository instance."""
        return BookingRepository(self._db)

    def create_offer_repository(self) -> OfferRepository:
        """Create an OfferRepository instance."""
        return OfferRepository(self._db)
