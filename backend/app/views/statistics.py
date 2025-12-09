from typing import Dict, List, Any, Literal
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.controllers.statistics_controller import StatisticsController
from app.dependencies import require_manager, get_db

router = APIRouter(prefix="/statistics", tags=["Statistics"])


@router.get("/dashboard", response_model=Dict[str, Any], dependencies=[Depends(require_manager)])
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard summary statistics (manager only)."""
    controller = StatisticsController(db)
    return await controller.get_dashboard_summary()


@router.get("/room-occupancy", response_model=List[Dict[str, Any]], dependencies=[Depends(require_manager)])
async def get_room_occupancy(
    db: AsyncSession = Depends(get_db)
):
    """Get room occupancy statistics (manager only)."""
    controller = StatisticsController(db)
    return await controller.get_room_occupancy()


@router.get("/financial", response_model=Dict[str, Any], dependencies=[Depends(require_manager)])
async def get_financial_metrics(
    db: AsyncSession = Depends(get_db)
):
    """Get financial metrics (manager only)."""
    controller = StatisticsController(db)
    return await controller.get_financial_metrics()


@router.get("/regular-customers", response_model=List[Dict[str, Any]], dependencies=[Depends(require_manager)])
async def get_regular_customers(
    db: AsyncSession = Depends(get_db)
):
    """Get regular customers information (manager only)."""
    controller = StatisticsController(db)
    return await controller.get_regular_customers()


@router.get("/graphs/revenue", response_model=List[Dict[str, Any]], dependencies=[Depends(require_manager)])
async def get_revenue_graph(
    period: Literal["day", "week", "month"] = Query(default="month", description="Time period grouping"),
    days: int = Query(default=30, ge=1, le=365, description="Number of days to look back"),
    db: AsyncSession = Depends(get_db)
):
    """Get revenue data over time for graphing (manager only)."""
    controller = StatisticsController(db)
    return await controller.get_revenue_over_time(period=period, days=days)


@router.get("/graphs/occupancy", response_model=List[Dict[str, Any]], dependencies=[Depends(require_manager)])
async def get_occupancy_graph(
    period: Literal["day", "week", "month"] = Query(default="month", description="Time period grouping"),
    days: int = Query(default=30, ge=1, le=365, description="Number of days to look back"),
    db: AsyncSession = Depends(get_db)
):
    """Get room occupancy data over time for graphing (manager only)."""
    controller = StatisticsController(db)
    return await controller.get_occupancy_over_time(period=period, days=days)


@router.get("/graphs/bookings-status", response_model=List[Dict[str, Any]], dependencies=[Depends(require_manager)])
async def get_bookings_status_graph(
    period: Literal["day", "week", "month"] = Query(default="month", description="Time period grouping"),
    days: int = Query(default=30, ge=1, le=365, description="Number of days to look back"),
    db: AsyncSession = Depends(get_db)
):
    """Get bookings by status over time for graphing (manager only)."""
    controller = StatisticsController(db)
    return await controller.get_bookings_by_status_over_time(period=period, days=days)
