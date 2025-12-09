from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.offer import Offer
from app.repositories.base import BaseRepository


class OfferRepository(BaseRepository[Offer]):
    """Repository for Offer model."""

    def __init__(self, db: AsyncSession):
        super().__init__(Offer, db)

    async def get_active_offers(self) -> List[Offer]:
        """Get all active offers."""
        result = await self.db.execute(
            select(Offer).where(Offer.is_active == True)
        )
        return list(result.scalars().all())

    async def get_global_offers(self) -> List[Offer]:
        """Get all global offers."""
        result = await self.db.execute(
            select(Offer).where(
                Offer.is_active == True,
                Offer.offer_type == "global"
            )
        )
        return list(result.scalars().all())

    async def get_by_name(self, name: str) -> Optional[Offer]:
        """Get offer by name."""
        result = await self.db.execute(select(Offer).where(Offer.name == name))
        return result.scalar_one_or_none()
