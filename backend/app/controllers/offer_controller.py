from typing import List
from fastapi import HTTPException, status
from app.repositories.offer_repository import OfferRepository
from app.models.offer import Offer
from app.schemas.offer import OfferCreate, OfferUpdate


class OfferController:
    """Controller for offer operations."""

    def __init__(self, offer_repo: OfferRepository):
        self.offer_repo = offer_repo

    async def get_offer(self, offer_id: int) -> Offer:
        """Get offer by ID."""
        offer = await self.offer_repo.get(offer_id)
        if not offer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Offer not found"
            )
        return offer

    async def get_all_offers(self, skip: int = 0, limit: int = 100) -> List[Offer]:
        """Get all offers."""
        return await self.offer_repo.get_all(skip, limit)

    async def get_active_offers(self) -> List[Offer]:
        """Get all active offers."""
        return await self.offer_repo.get_active_offers()

    async def get_global_offers(self) -> List[Offer]:
        """Get all global offers."""
        return await self.offer_repo.get_global_offers()

    async def create_offer(self, offer_data: OfferCreate) -> Offer:
        """Create a new offer."""
        # Check if offer name already exists
        existing = await self.offer_repo.get_by_name(offer_data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Offer name already exists"
            )

        offer = Offer(**offer_data.model_dump())
        return await self.offer_repo.create(offer)

    async def update_offer(self, offer_id: int, offer_data: OfferUpdate) -> Offer:
        """Update offer."""
        offer = await self.offer_repo.get(offer_id)
        if not offer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Offer not found"
            )

        # Update fields
        update_data = offer_data.model_dump(exclude_unset=True)

        if "name" in update_data:
            existing = await self.offer_repo.get_by_name(update_data["name"])
            if existing and existing.id != offer_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Offer name already exists"
                )

        for field, value in update_data.items():
            setattr(offer, field, value)

        return await self.offer_repo.update(offer)

    async def delete_offer(self, offer_id: int) -> None:
        """Delete offer."""
        offer = await self.offer_repo.get(offer_id)
        if not offer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Offer not found"
            )
        await self.offer_repo.delete(offer)
