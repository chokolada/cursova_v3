"""Add historical bookings for September, October, and November 2025."""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.booking import Booking, BookingStatus
from app.models.room import Room
from app.models.user import User


async def add_historical_bookings():
    """Add bookings for September, October, and November 2025."""
    async with AsyncSessionLocal() as db:
        # Get users
        result = await db.execute(select(User))
        users = list(result.scalars().all())

        if not users:
            print("No users found! Run seed_database_with_offers.py first.")
            return

        # Get rooms
        result = await db.execute(select(Room))
        rooms = list(result.scalars().all())

        if not rooms:
            print("No rooms found! Run seed_database_with_offers.py first.")
            return

        print(f"Found {len(users)} users and {len(rooms)} rooms")

        # Define bookings for each month
        bookings_data = [
            # September 2025 - 8 bookings
            {
                "month": 9,
                "bookings": [
                    {"user_idx": 0, "room_idx": 0, "days": 3, "day_offset": 5},
                    {"user_idx": 1, "room_idx": 1, "days": 2, "day_offset": 8},
                    {"user_idx": 2, "room_idx": 2, "days": 4, "day_offset": 12},
                    {"user_idx": 0, "room_idx": 3, "days": 1, "day_offset": 15},
                    {"user_idx": 1, "room_idx": 4, "days": 3, "day_offset": 18},
                    {"user_idx": 2, "room_idx": 5, "days": 2, "day_offset": 22},
                    {"user_idx": 0, "room_idx": 0, "days": 4, "day_offset": 25},
                    {"user_idx": 1, "room_idx": 1, "days": 2, "day_offset": 28},
                ]
            },
            # October 2025 - 12 bookings
            {
                "month": 10,
                "bookings": [
                    {"user_idx": 0, "room_idx": 0, "days": 3, "day_offset": 2},
                    {"user_idx": 1, "room_idx": 1, "days": 2, "day_offset": 5},
                    {"user_idx": 2, "room_idx": 2, "days": 4, "day_offset": 8},
                    {"user_idx": 0, "room_idx": 3, "days": 2, "day_offset": 10},
                    {"user_idx": 1, "room_idx": 4, "days": 3, "day_offset": 13},
                    {"user_idx": 2, "room_idx": 5, "days": 2, "day_offset": 16},
                    {"user_idx": 0, "room_idx": 0, "days": 4, "day_offset": 19},
                    {"user_idx": 1, "room_idx": 1, "days": 2, "day_offset": 21},
                    {"user_idx": 2, "room_idx": 2, "days": 3, "day_offset": 23},
                    {"user_idx": 0, "room_idx": 3, "days": 2, "day_offset": 25},
                    {"user_idx": 1, "room_idx": 4, "days": 1, "day_offset": 27},
                    {"user_idx": 2, "room_idx": 5, "days": 3, "day_offset": 29},
                ]
            },
            # November 2025 - 15 bookings
            {
                "month": 11,
                "bookings": [
                    {"user_idx": 0, "room_idx": 0, "days": 3, "day_offset": 1},
                    {"user_idx": 1, "room_idx": 1, "days": 2, "day_offset": 3},
                    {"user_idx": 2, "room_idx": 2, "days": 4, "day_offset": 5},
                    {"user_idx": 0, "room_idx": 3, "days": 2, "day_offset": 7},
                    {"user_idx": 1, "room_idx": 4, "days": 3, "day_offset": 9},
                    {"user_idx": 2, "room_idx": 5, "days": 2, "day_offset": 11},
                    {"user_idx": 0, "room_idx": 0, "days": 4, "day_offset": 13},
                    {"user_idx": 1, "room_idx": 1, "days": 2, "day_offset": 15},
                    {"user_idx": 2, "room_idx": 2, "days": 3, "day_offset": 17},
                    {"user_idx": 0, "room_idx": 3, "days": 2, "day_offset": 19},
                    {"user_idx": 1, "room_idx": 4, "days": 1, "day_offset": 21},
                    {"user_idx": 2, "room_idx": 5, "days": 3, "day_offset": 23},
                    {"user_idx": 0, "room_idx": 0, "days": 2, "day_offset": 25},
                    {"user_idx": 1, "room_idx": 1, "days": 4, "day_offset": 27},
                    {"user_idx": 2, "room_idx": 2, "days": 2, "day_offset": 29},
                ]
            },
        ]

        created_count = 0

        for month_data in bookings_data:
            month = month_data["month"]
            print(f"\nAdding bookings for {datetime(2025, month, 1).strftime('%B %Y')}...")

            for booking_info in month_data["bookings"]:
                user = users[booking_info["user_idx"] % len(users)]
                room = rooms[booking_info["room_idx"] % len(rooms)]

                check_in = datetime(2025, month, booking_info["day_offset"])
                check_out = check_in + timedelta(days=booking_info["days"])

                total_price = room.price_per_night * booking_info["days"]

                booking = Booking(
                    user_id=user.id,
                    room_id=room.id,
                    check_in_date=check_in,
                    check_out_date=check_out,
                    guests_count=2,
                    total_price=total_price,
                    status=BookingStatus.COMPLETED,
                    special_requests="Historical test data",
                    created_at=check_in - timedelta(days=7)  # Created 7 days before check-in
                )

                db.add(booking)
                created_count += 1

            await db.commit()
            print(f"  Added {len(month_data['bookings'])} bookings for {datetime(2025, month, 1).strftime('%B')}")

        print(f"\n✅ Successfully added {created_count} historical bookings!")

        # Show summary
        print("\nBookings Summary:")
        print("  September 2025: 8 bookings")
        print("  October 2025: 12 bookings")
        print("  November 2025: 15 bookings")
        print("  December 2025: ~19 bookings (existing)")
        print(f"  Total: ~{created_count + 19} bookings")


if __name__ == "__main__":
    asyncio.run(add_historical_bookings())
