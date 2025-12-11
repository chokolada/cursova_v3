from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterable, Optional
from app.models.offer import Offer
from app.models.room import Room


class BasePricingStrategy(ABC):
    """Strategy interface for calculating booking totals."""

    @abstractmethod
    def calculate_total(self, room: Room, check_in: datetime, check_out: datetime, offers: Optional[Iterable[Offer]] = None) -> float:
        """Return total price for a booking."""


class StandardPricingStrategy(BasePricingStrategy):
    """Default strategy: nightly rate multiplied by duration plus offers."""

    def calculate_total(self, room: Room, check_in: datetime, check_out: datetime, offers: Optional[Iterable[Offer]] = None) -> float:
        days = (check_out - check_in).days
        if days <= 0:
            raise ValueError("Check-out date must be after check-in date")

        total = room.price_per_night * days
        if offers:
            total += sum((offer.price for offer in offers if offer is not None), 0)
        return float(total)


class LongStayDiscountStrategy(StandardPricingStrategy):
    """Strategy that applies a discount for longer stays."""

    def __init__(self, threshold_days: int = 7, discount_rate: float = 0.1):
        self.threshold_days = threshold_days
        self.discount_rate = discount_rate

    def calculate_total(self, room: Room, check_in: datetime, check_out: datetime, offers: Optional[Iterable[Offer]] = None) -> float:
        total = super().calculate_total(room, check_in, check_out, offers)
        days = (check_out - check_in).days
        if days >= self.threshold_days:
            total *= (1 - self.discount_rate)
        return float(total)


class PricingContext:
    """Context for selecting and executing pricing strategies."""

    def __init__(self, strategy: BasePricingStrategy):
        self.strategy = strategy

    def calculate(self, room: Room, check_in: datetime, check_out: datetime, offers: Optional[Iterable[Offer]] = None) -> float:
        return self.strategy.calculate_total(room, check_in, check_out, offers)
