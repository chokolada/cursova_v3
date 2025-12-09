from typing import Dict, List, Any
from fastapi import APIRouter, Depends
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
