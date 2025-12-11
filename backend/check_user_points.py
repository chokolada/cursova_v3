"""Check user bonus points calculation."""
import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.booking import Booking, BookingStatus
from app.models.user import User


async def check_user_points():
    """Check all bookings for john_doe and calculate points."""
    async with AsyncSessionLocal() as db:
        # Get john_doe user
        result = await db.execute(
            select(User).where(User.username == 'john_doe')
        )
        user = result.scalar_one_or_none()

        if not user:
            print('User john_doe not found')
            return

        print(f'Current bonus_points in database: {user.bonus_points}')
        print(f'\nFetching all bookings for john_doe (user_id={user.id})...\n')

        # Get ALL bookings for john_doe
        result = await db.execute(
            select(Booking).where(Booking.user_id == user.id)
        )
        bookings = list(result.scalars().all())

        print(f'Total bookings: {len(bookings)}\n')

        total_points_all = 0
        total_points_completed = 0

        for booking in bookings:
            points = int(booking.total_price // 10)
            total_points_all += points
            if booking.status == BookingStatus.COMPLETED:
                total_points_completed += points
            print(f'Booking {booking.id}: Status={booking.status.value}, Price=${booking.total_price:.2f}, Points={points}')

        print(f'\n--- Summary ---')
        print(f'Total calculated points (ALL bookings): {total_points_all}')
        print(f'Total calculated points (COMPLETED only): {total_points_completed}')
        print(f'Current database points: {user.bonus_points}')
        print(f'Difference (vs COMPLETED): {total_points_completed - user.bonus_points}')
        print(f'Difference (vs ALL): {total_points_all - user.bonus_points}')


if __name__ == "__main__":
    asyncio.run(check_user_points())
