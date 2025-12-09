from typing import List
from fastapi import APIRouter, Depends, status
from app.controllers.offer_controller import OfferController
from app.schemas.offer import OfferCreate, OfferUpdate, OfferResponse
from app.dependencies import get_offer_repository, require_manager
from app.repositories.offer_repository import OfferRepository

router = APIRouter(prefix="/offers", tags=["Offers"])


@router.get("/", response_model=List[OfferResponse])
async def get_all_offers(
    skip: int = 0,
    limit: int = 100,
    offer_repo: OfferRepository = Depends(get_offer_repository)
):
    """Get all offers."""
    controller = OfferController(offer_repo)
    return await controller.get_all_offers(skip, limit)


@router.get("/active", response_model=List[OfferResponse])
async def get_active_offers(
    offer_repo: OfferRepository = Depends(get_offer_repository)
):
    """Get all active offers."""
    controller = OfferController(offer_repo)
    return await controller.get_active_offers()


@router.get("/global", response_model=List[OfferResponse])
async def get_global_offers(
    offer_repo: OfferRepository = Depends(get_offer_repository)
):
    """Get all global offers."""
    controller = OfferController(offer_repo)
    return await controller.get_global_offers()


@router.get("/{offer_id}", response_model=OfferResponse)
async def get_offer(
    offer_id: int,
    offer_repo: OfferRepository = Depends(get_offer_repository)
):
    """Get offer by ID."""
    controller = OfferController(offer_repo)
    return await controller.get_offer(offer_id)


@router.post("/", response_model=OfferResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_manager)])
async def create_offer(
    offer_data: OfferCreate,
    offer_repo: OfferRepository = Depends(get_offer_repository)
):
    """Create a new offer (manager only)."""
    controller = OfferController(offer_repo)
    return await controller.create_offer(offer_data)


@router.put("/{offer_id}", response_model=OfferResponse, dependencies=[Depends(require_manager)])
async def update_offer(
    offer_id: int,
    offer_data: OfferUpdate,
    offer_repo: OfferRepository = Depends(get_offer_repository)
):
    """Update offer (manager only)."""
    controller = OfferController(offer_repo)
    return await controller.update_offer(offer_id, offer_data)


@router.delete("/{offer_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_manager)])
async def delete_offer(
    offer_id: int,
    offer_repo: OfferRepository = Depends(get_offer_repository)
):
    """Delete offer (manager only)."""
    controller = OfferController(offer_repo)
    await controller.delete_offer(offer_id)
