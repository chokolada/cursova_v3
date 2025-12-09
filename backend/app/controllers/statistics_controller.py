from typing import Dict, List, Any
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, extract
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.booking import Booking, BookingStatus
from app.models.room import Room
from app.models.user import User


class StatisticsController:
    """Controller for statistics and analytics."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_room_occupancy(self) -> List[Dict[str, Any]]:
        """Calculate room occupancy statistics."""
        # Get all rooms with their booking counts
        result = await self.db.execute(
            select(
                Room.id,
                Room.room_number,
                Room.room_type,
                Room.is_available,
                func.count(Booking.id).label('total_bookings'),
                func.count(
                    func.nullif(
                        (Booking.status == BookingStatus.CONFIRMED) |
                        (Booking.status == BookingStatus.COMPLETED),
                        False
                    )
                ).label('confirmed_bookings')
            )
            .outerjoin(Booking, Room.id == Booking.room_id)
            .group_by(Room.id)
            .order_by(func.count(Booking.id).desc())
        )

        rooms = result.all()

        occupancy_data = []
        for room in rooms:
            occupancy_data.append({
                'room_id': room.id,
                'room_number': room.room_number,
                'room_type': room.room_type,
                'is_available': room.is_available,
                'total_bookings': room.total_bookings or 0,
                'confirmed_bookings': room.confirmed_bookings or 0,
            })

        return occupancy_data

    async def get_financial_metrics(self) -> Dict[str, Any]:
        """Calculate financial metrics."""
        # Revenue by month (last 12 months)
        twelve_months_ago = datetime.utcnow() - timedelta(days=365)

        result = await self.db.execute(
            select(
                extract('year', Booking.created_at).label('year'),
                extract('month', Booking.created_at).label('month'),
                func.sum(Booking.total_price).label('revenue'),
                func.count(Booking.id).label('booking_count')
            )
            .where(
                and_(
                    Booking.created_at >= twelve_months_ago,
                    Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED])
                )
            )
            .group_by(
                extract('year', Booking.created_at),
                extract('month', Booking.created_at)
            )
            .order_by(
                extract('year', Booking.created_at),
                extract('month', Booking.created_at)
            )
        )

        monthly_revenue = []
        for row in result.all():
            monthly_revenue.append({
                'year': int(row.year),
                'month': int(row.month),
                'revenue': float(row.revenue or 0),
                'booking_count': row.booking_count or 0
            })

        # Room type popularity
        result = await self.db.execute(
            select(
                Room.room_type,
                func.count(Booking.id).label('booking_count'),
                func.sum(Booking.total_price).label('total_revenue'),
                func.avg(Booking.total_price).label('avg_price')
            )
            .join(Booking, Room.id == Booking.room_id)
            .where(Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED]))
            .group_by(Room.room_type)
            .order_by(func.count(Booking.id).desc())
        )

        room_type_popularity = []
        for row in result.all():
            room_type_popularity.append({
                'room_type': row.room_type,
                'booking_count': row.booking_count or 0,
                'total_revenue': float(row.total_revenue or 0),
                'avg_price': float(row.avg_price or 0)
            })

        # Total statistics
        result = await self.db.execute(
            select(
                func.sum(Booking.total_price).label('total_revenue'),
                func.count(Booking.id).label('total_bookings')
            )
            .where(Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED]))
        )

        totals = result.one()

        return {
            'monthly_revenue': monthly_revenue,
            'room_type_popularity': room_type_popularity,
            'total_revenue': float(totals.total_revenue or 0),
            'total_bookings': totals.total_bookings or 0
        }

    async def get_regular_customers(self) -> List[Dict[str, Any]]:
        """Get information about regular customers."""
        # Customers with multiple bookings
        result = await self.db.execute(
            select(
                User.id,
                User.username,
                User.email,
                User.full_name,
                func.count(Booking.id).label('booking_count'),
                func.sum(Booking.total_price).label('total_spent'),
                func.max(Booking.created_at).label('last_booking_date')
            )
            .join(Booking, User.id == Booking.user_id)
            .group_by(User.id)
            .having(func.count(Booking.id) >= 2)
            .order_by(func.count(Booking.id).desc())
            .limit(50)
        )

        regular_customers = []
        for row in result.all():
            regular_customers.append({
                'user_id': row.id,
                'username': row.username,
                'email': row.email,
                'full_name': row.full_name,
                'booking_count': row.booking_count or 0,
                'total_spent': float(row.total_spent or 0),
                'last_booking_date': row.last_booking_date.isoformat() if row.last_booking_date else None
            })

        return regular_customers

    async def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get summary statistics for dashboard."""
        # Total rooms
        rooms_result = await self.db.execute(
            select(
                func.count(Room.id).label('total_rooms'),
                func.count(func.nullif(Room.is_available, False)).label('available_rooms')
            )
        )
        rooms_stats = rooms_result.one()

        # Total bookings by status
        bookings_result = await self.db.execute(
            select(
                Booking.status,
                func.count(Booking.id).label('count')
            )
            .group_by(Booking.status)
        )

        bookings_by_status = {}
        for row in bookings_result.all():
            bookings_by_status[row.status.value] = row.count

        # Total users
        users_result = await self.db.execute(
            select(func.count(User.id))
        )
        total_users = users_result.scalar()

        # Current month revenue
        current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        revenue_result = await self.db.execute(
            select(func.sum(Booking.total_price))
            .where(
                and_(
                    Booking.created_at >= current_month_start,
                    Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED])
                )
            )
        )
        current_month_revenue = revenue_result.scalar() or 0

        return {
            'total_rooms': rooms_stats.total_rooms or 0,
            'available_rooms': rooms_stats.available_rooms or 0,
            'occupied_rooms': (rooms_stats.total_rooms or 0) - (rooms_stats.available_rooms or 0),
            'bookings_by_status': bookings_by_status,
            'total_users': total_users or 0,
            'current_month_revenue': float(current_month_revenue)
        }
