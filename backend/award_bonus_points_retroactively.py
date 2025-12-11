"""Retroactively award bonus points for all completed bookings."""
import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.booking import Booking, BookingStatus
from app.models.user import User


async def award_bonus_points_retroactively():
    """Award bonus points for all completed bookings."""
    async with AsyncSessionLocal() as db:
        # Get all completed bookings
        result = await db.execute(
            select(Booking).where(Booking.status == BookingStatus.COMPLETED)
        )
        completed_bookings = list(result.scalars().all())

        print(f"Found {len(completed_bookings)} completed bookings")

        # Group bookings by user
        user_points = {}
        for booking in completed_bookings:
            bonus_points = int(booking.total_price // 10)
            if booking.user_id not in user_points:
                user_points[booking.user_id] = 0
            user_points[booking.user_id] += bonus_points

        print(f"\nAwarding points to {len(user_points)} users...")

        # Award points to each user
        for user_id, points in user_points.items():
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()

            if user:
                user.bonus_points += points
                print(f"  {user.username}: +{points} points (total: {user.bonus_points})")

        await db.commit()
        print(f"\n[SUCCESS] Bonus points awarded successfully!")

        # Show summary
        print("\nSummary:")
        result = await db.execute(
            select(User).where(User.bonus_points > 0)
        )
        users_with_points = list(result.scalars().all())

        for user in users_with_points:
            print(f"  {user.username}: {user.bonus_points} points")


if __name__ == "__main__":
    asyncio.run(award_bonus_points_retroactively())
