from typing import Dict, List, Any, Literal
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, extract, case
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.booking import Booking, BookingStatus
from app.models.room import Room
from app.models.user import User
from app.services.statistics_builder import StatisticsResponseBuilder

PeriodType = Literal["day", "week", "month"]


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

    async def get_room_category_popularity(self) -> List[Dict[str, Any]]:
        """Get popularity statistics for room categories (types)."""
        # Count bookings by room type
        result = await self.db.execute(
            select(
                Room.room_type,
                func.count(Booking.id).label('booking_count'),
                func.sum(Booking.total_price).label('total_revenue'),
                func.count(func.distinct(Booking.user_id)).label('unique_customers')
            )
            .join(Booking, Room.id == Booking.room_id)
            .where(Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED]))
            .group_by(Room.room_type)
            .order_by(func.count(Booking.id).desc())
        )

        categories = result.all()

        # Calculate total bookings for percentage
        total_bookings = sum(cat.booking_count for cat in categories)

        category_data = []
        for cat in categories:
            percentage = (cat.booking_count / total_bookings * 100) if total_bookings > 0 else 0
            category_data.append({
                'room_type': cat.room_type,
                'booking_count': cat.booking_count,
                'total_revenue': float(cat.total_revenue or 0),
                'unique_customers': cat.unique_customers or 0,
                'percentage': round(percentage, 1)
            })

        return category_data

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

        builder = (
            StatisticsResponseBuilder()
            .with_room_overview(rooms_stats.total_rooms or 0, rooms_stats.available_rooms or 0)
            .with_bookings_by_status(bookings_by_status)
            .with_user_total(total_users or 0)
            .with_current_revenue(float(current_month_revenue))
        )

        return builder.build()

    async def get_revenue_over_time(
        self,
        period: PeriodType = "month",
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get revenue data over time for graphing.

        Args:
            period: Grouping period - 'day', 'week', or 'month'
            days: Number of days to look back (default 30)
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        if period == "day":
            # Group by day
            result = await self.db.execute(
                select(
                    func.date(Booking.created_at).label('period'),
                    func.sum(Booking.total_price).label('revenue'),
                    func.count(Booking.id).label('booking_count')
                )
                .where(
                    and_(
                        Booking.created_at >= start_date,
                        Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED])
                    )
                )
                .group_by(func.date(Booking.created_at))
                .order_by(func.date(Booking.created_at))
            )
        elif period == "week":
            # Group by week (year + week number)
            result = await self.db.execute(
                select(
                    func.strftime('%Y-W%W', Booking.created_at).label('period'),
                    func.sum(Booking.total_price).label('revenue'),
                    func.count(Booking.id).label('booking_count')
                )
                .where(
                    and_(
                        Booking.created_at >= start_date,
                        Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED])
                    )
                )
                .group_by(func.strftime('%Y-W%W', Booking.created_at))
                .order_by(func.strftime('%Y-W%W', Booking.created_at))
            )
        else:  # month
            # Group by month (year + month)
            result = await self.db.execute(
                select(
                    func.strftime('%Y-%m', Booking.created_at).label('period'),
                    func.sum(Booking.total_price).label('revenue'),
                    func.count(Booking.id).label('booking_count')
                )
                .where(
                    and_(
                        Booking.created_at >= start_date,
                        Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED])
                    )
                )
                .group_by(func.strftime('%Y-%m', Booking.created_at))
                .order_by(func.strftime('%Y-%m', Booking.created_at))
            )

        # Collect data from query
        data_dict = {}
        for row in result.all():
            data_dict[str(row.period)] = {
                'period': str(row.period),
                'revenue': float(row.revenue or 0),
                'booking_count': row.booking_count or 0
            }

        # Fill in missing periods with zero values for better visualization
        filled_data = []
        current_date = start_date
        end_date = datetime.utcnow()

        if period == "day":
            while current_date <= end_date:
                period_str = current_date.strftime('%Y-%m-%d')
                if period_str in data_dict:
                    filled_data.append(data_dict[period_str])
                else:
                    filled_data.append({
                        'period': period_str,
                        'revenue': 0,
                        'booking_count': 0
                    })
                current_date += timedelta(days=1)
        elif period == "week":
            while current_date <= end_date:
                period_str = current_date.strftime('%Y-W%W')
                if period_str in data_dict:
                    filled_data.append(data_dict[period_str])
                    # Move to next week
                    current_date += timedelta(weeks=1)
                else:
                    filled_data.append({
                        'period': period_str,
                        'revenue': 0,
                        'booking_count': 0
                    })
                    current_date += timedelta(weeks=1)
        else:  # month
            while current_date <= end_date:
                period_str = current_date.strftime('%Y-%m')
                if period_str in data_dict:
                    filled_data.append(data_dict[period_str])
                else:
                    filled_data.append({
                        'period': period_str,
                        'revenue': 0,
                        'booking_count': 0
                    })
                # Move to first day of next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1, day=1)

        return filled_data

    async def get_occupancy_over_time(
        self,
        period: PeriodType = "month",
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get room occupancy statistics over time for graphing.

        Args:
            period: Grouping period - 'day', 'week', or 'month'
            days: Number of days to look back (default 30)
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        # Get total rooms (constant)
        rooms_result = await self.db.execute(
            select(func.count(Room.id))
        )
        total_rooms = rooms_result.scalar() or 0

        if period == "day":
            # Group by day
            result = await self.db.execute(
                select(
                    func.date(Booking.check_in_date).label('period'),
                    func.count(func.distinct(Booking.room_id)).label('occupied_rooms'),
                    func.count(Booking.id).label('booking_count')
                )
                .where(
                    and_(
                        Booking.check_in_date >= start_date,
                        Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED])
                    )
                )
                .group_by(func.date(Booking.check_in_date))
                .order_by(func.date(Booking.check_in_date))
            )
        elif period == "week":
            # Group by week
            result = await self.db.execute(
                select(
                    func.strftime('%Y-W%W', Booking.check_in_date).label('period'),
                    func.count(func.distinct(Booking.room_id)).label('occupied_rooms'),
                    func.count(Booking.id).label('booking_count')
                )
                .where(
                    and_(
                        Booking.check_in_date >= start_date,
                        Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED])
                    )
                )
                .group_by(func.strftime('%Y-W%W', Booking.check_in_date))
                .order_by(func.strftime('%Y-W%W', Booking.check_in_date))
            )
        else:  # month
            # Group by month
            result = await self.db.execute(
                select(
                    func.strftime('%Y-%m', Booking.check_in_date).label('period'),
                    func.count(func.distinct(Booking.room_id)).label('occupied_rooms'),
                    func.count(Booking.id).label('booking_count')
                )
                .where(
                    and_(
                        Booking.check_in_date >= start_date,
                        Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED])
                    )
                )
                .group_by(func.strftime('%Y-%m', Booking.check_in_date))
                .order_by(func.strftime('%Y-%m', Booking.check_in_date))
            )

        # Collect data from query
        data_dict = {}
        for row in result.all():
            occupied = row.occupied_rooms or 0
            occupancy_rate = (occupied / total_rooms * 100) if total_rooms > 0 else 0
            data_dict[str(row.period)] = {
                'period': str(row.period),
                'occupied_rooms': occupied,
                'total_rooms': total_rooms,
                'occupancy_rate': round(occupancy_rate, 2),
                'booking_count': row.booking_count or 0
            }

        # Fill in missing periods with zero values for better visualization
        filled_data = []
        current_date = start_date
        end_date = datetime.utcnow()

        if period == "day":
            while current_date <= end_date:
                period_str = current_date.strftime('%Y-%m-%d')
                if period_str in data_dict:
                    filled_data.append(data_dict[period_str])
                else:
                    filled_data.append({
                        'period': period_str,
                        'occupied_rooms': 0,
                        'total_rooms': total_rooms,
                        'occupancy_rate': 0.0,
                        'booking_count': 0
                    })
                current_date += timedelta(days=1)
        elif period == "week":
            while current_date <= end_date:
                period_str = current_date.strftime('%Y-W%W')
                if period_str in data_dict:
                    filled_data.append(data_dict[period_str])
                else:
                    filled_data.append({
                        'period': period_str,
                        'occupied_rooms': 0,
                        'total_rooms': total_rooms,
                        'occupancy_rate': 0.0,
                        'booking_count': 0
                    })
                current_date += timedelta(weeks=1)
        else:  # month
            while current_date <= end_date:
                period_str = current_date.strftime('%Y-%m')
                if period_str in data_dict:
                    filled_data.append(data_dict[period_str])
                else:
                    filled_data.append({
                        'period': period_str,
                        'occupied_rooms': 0,
                        'total_rooms': total_rooms,
                        'occupancy_rate': 0.0,
                        'booking_count': 0
                    })
                # Move to first day of next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1, day=1)

        return filled_data

    async def get_bookings_by_status_over_time(
        self,
        period: PeriodType = "month",
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get booking counts by status over time for graphing.

        Args:
            period: Grouping period - 'day', 'week', or 'month'
            days: Number of days to look back (default 30)
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        if period == "day":
            period_expr = func.date(Booking.created_at)
        elif period == "week":
            period_expr = func.strftime('%Y-W%W', Booking.created_at)
        else:  # month
            period_expr = func.strftime('%Y-%m', Booking.created_at)

        result = await self.db.execute(
            select(
                period_expr.label('period'),
                Booking.status,
                func.count(Booking.id).label('count')
            )
            .where(Booking.created_at >= start_date)
            .group_by(period_expr, Booking.status)
            .order_by(period_expr)
        )

        # Organize data by period
        data_by_period = {}
        for row in result.all():
            period_str = str(row.period)
            if period_str not in data_by_period:
                data_by_period[period_str] = {
                    'period': period_str,
                    'pending': 0,
                    'confirmed': 0,
                    'cancelled': 0,
                    'completed': 0
                }
            data_by_period[period_str][row.status.value] = row.count

        # Fill in missing periods with zero values for better visualization
        filled_data = []
        current_date = start_date
        end_date = datetime.utcnow()

        if period == "day":
            while current_date <= end_date:
                period_str = current_date.strftime('%Y-%m-%d')
                if period_str in data_by_period:
                    filled_data.append(data_by_period[period_str])
                else:
                    filled_data.append({
                        'period': period_str,
                        'pending': 0,
                        'confirmed': 0,
                        'cancelled': 0,
                        'completed': 0
                    })
                current_date += timedelta(days=1)
        elif period == "week":
            while current_date <= end_date:
                period_str = current_date.strftime('%Y-W%W')
                if period_str in data_by_period:
                    filled_data.append(data_by_period[period_str])
                else:
                    filled_data.append({
                        'period': period_str,
                        'pending': 0,
                        'confirmed': 0,
                        'cancelled': 0,
                        'completed': 0
                    })
                current_date += timedelta(weeks=1)
        else:  # month
            while current_date <= end_date:
                period_str = current_date.strftime('%Y-%m')
                if period_str in data_by_period:
                    filled_data.append(data_by_period[period_str])
                else:
                    filled_data.append({
                        'period': period_str,
                        'pending': 0,
                        'confirmed': 0,
                        'cancelled': 0,
                        'completed': 0
                    })
                # Move to first day of next month
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1, day=1)

        return filled_data
