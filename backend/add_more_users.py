"""
Script to add more regular users with varying amounts of booking data.
Creates regular customers (10+ completed bookings) and casual users.
"""
import asyncio
import random
from datetime import datetime, timedelta
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.room import Room
from app.models.booking import Booking, BookingStatus
from app.models.offer import Offer
from app.core.security import get_password_hash


async def create_additional_users():
    """Create additional test users."""
    async with AsyncSessionLocal() as session:
        users_data = [
            # Regular customers (will get 10+ completed bookings)
            {
                "username": "sarah_johnson",
                "email": "sarah.j@example.com",
                "password": "User123!",
                "full_name": "Sarah Johnson",
                "role": UserRole.USER,
                "booking_count": 12,  # Regular customer
                "is_regular": True
            },
            {
                "username": "mike_brown",
                "email": "mike.b@example.com",
                "password": "User123!",
                "full_name": "Mike Brown",
                "role": UserRole.USER,
                "booking_count": 15,  # Regular customer
                "is_regular": True
            },
            {
                "username": "emma_davis",
                "email": "emma.d@example.com",
                "password": "User123!",
                "full_name": "Emma Davis",
                "role": UserRole.USER,
                "booking_count": 11,  # Regular customer
                "is_regular": True
            },
            # Casual users (less than 10 bookings)
            {
                "username": "alex_martinez",
                "email": "alex.m@example.com",
                "password": "User123!",
                "full_name": "Alex Martinez",
                "role": UserRole.USER,
                "booking_count": 5,
                "is_regular": False
            },
            {
                "username": "lisa_anderson",
                "email": "lisa.a@example.com",
                "password": "User123!",
                "full_name": "Lisa Anderson",
                "role": UserRole.USER,
                "booking_count": 3,
                "is_regular": False
            },
            {
                "username": "tom_wilson",
                "email": "tom.w@example.com",
                "password": "User123!",
                "full_name": "Tom Wilson",
                "role": UserRole.USER,
                "booking_count": 2,
                "is_regular": False
            },
            {
                "username": "rachel_lee",
                "email": "rachel.l@example.com",
                "password": "User123!",
                "full_name": "Rachel Lee",
                "role": UserRole.USER,
                "booking_count": 1,
                "is_regular": False
            }
        ]

        created_users = []
        users_with_booking_count = []

        for user_data in users_data:
            # Check if user already exists
            result = await session.execute(
                select(User).where(User.username == user_data["username"])
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                # User exists, check if they have bookings
                result = await session.execute(
                    select(Booking).where(Booking.user_id == existing_user.id)
                )
                existing_bookings = list(result.scalars().all())

                if existing_bookings:
                    print(f"  User {user_data['username']} already exists with bookings, skipping...")
                    continue
                else:
                    # User exists but has no bookings, we'll add bookings for them
                    print(f"  User {user_data['username']} exists but has no bookings, adding bookings...")
                    users_with_booking_count.append({
                        "user": existing_user,
                        "booking_count": user_data["booking_count"],
                        "is_regular": user_data["is_regular"]
                    })
                continue

            user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                full_name=user_data["full_name"],
                role=user_data["role"],
                is_active=True,
                bonus_points=0
            )
            session.add(user)
            await session.flush()  # Flush to get the user ID

            created_users.append(user_data["username"])
            users_with_booking_count.append({
                "user": user,
                "booking_count": user_data["booking_count"],
                "is_regular": user_data["is_regular"]
            })

        await session.commit()
        print(f"[OK] Created {len(created_users)} new users: {', '.join(created_users)}")

        return users_with_booking_count


async def create_bookings_for_users(users_with_booking_count):
    """Create bookings for the new users."""
    async with AsyncSessionLocal() as session:
        # Get all rooms
        result = await session.execute(select(Room))
        rooms = list(result.scalars().all())

        if not rooms:
            print("[ERROR] No rooms found in database. Please run seed_database_with_offers.py first.")
            return

        # Get all offers
        result = await session.execute(select(Offer))
        offers = list(result.scalars().all())

        total_bookings_created = 0
        total_bonus_points = 0

        for user_info in users_with_booking_count:
            user = user_info["user"]
            booking_count = user_info["booking_count"]
            is_regular = user_info["is_regular"]

            user_bonus_points = 0
            bookings_created = 0

            # Generate bookings spread over the past year
            base_date = datetime.now() - timedelta(days=365)

            for i in range(booking_count):
                # Random room
                room = random.choice(rooms)

                # Create bookings at various dates in the past
                days_offset = i * (365 // booking_count) + random.randint(0, 15)
                check_in = base_date + timedelta(days=days_offset)

                # Random stay duration (1-7 days)
                stay_duration = random.randint(1, 7)
                check_out = check_in + timedelta(days=stay_duration)

                # Random guests count (1-4)
                guests = random.randint(1, min(4, room.capacity))

                # Calculate price (without offers for simplicity)
                total_price = stay_duration * room.price_per_night

                # Determine status
                # For regular customers: 80% completed, 15% confirmed, 5% cancelled
                # For casual users: 60% completed, 25% confirmed, 15% cancelled
                if is_regular:
                    status_roll = random.random()
                    if status_roll < 0.80:
                        status = BookingStatus.COMPLETED
                    elif status_roll < 0.95:
                        status = BookingStatus.CONFIRMED
                    else:
                        status = BookingStatus.CANCELLED
                else:
                    status_roll = random.random()
                    if status_roll < 0.60:
                        status = BookingStatus.COMPLETED
                    elif status_roll < 0.85:
                        status = BookingStatus.CONFIRMED
                    else:
                        status = BookingStatus.CANCELLED

                # Create booking
                booking = Booking(
                    user_id=user.id,
                    room_id=room.id,
                    check_in_date=check_in,
                    check_out_date=check_out,
                    guests_count=guests,
                    total_price=total_price,
                    status=status,
                    special_requests=random.choice([
                        None,
                        "Late check-in",
                        "High floor preferred",
                        "Quiet room please",
                        "Extra pillows",
                        None,
                        None
                    ])
                )

                session.add(booking)
                await session.flush()

                # Calculate bonus points for completed bookings
                if status == BookingStatus.COMPLETED:
                    points = int(total_price // 10)
                    user_bonus_points += points

                bookings_created += 1

            # Update user's bonus points
            user.bonus_points = user_bonus_points
            total_bonus_points += user_bonus_points
            total_bookings_created += bookings_created

            user_type = "Regular Customer" if is_regular else "Casual User"
            print(f"  {user.username} ({user_type}): {bookings_created} bookings, {user_bonus_points} bonus points")

        await session.commit()
        print(f"\n[OK] Created {total_bookings_created} bookings")
        print(f"[OK] Awarded {total_bonus_points} total bonus points")


async def show_summary():
    """Show summary of all users and their booking statistics."""
    async with AsyncSessionLocal() as session:
        # Get all users with booking counts
        result = await session.execute(
            select(User).where(User.role == UserRole.USER)
        )
        users = list(result.scalars().all())

        print("\n" + "="*70)
        print("USER SUMMARY")
        print("="*70)
        print(f"{'Username':<20} {'Bookings':<12} {'Bonus Points':<15} {'Type'}")
        print("-"*70)

        for user in users:
            result = await session.execute(
                select(Booking).where(Booking.user_id == user.id)
            )
            all_bookings = list(result.scalars().all())
            total_bookings = len(all_bookings)

            completed_bookings = [b for b in all_bookings if b.status == BookingStatus.COMPLETED]
            completed_count = len(completed_bookings)

            user_type = "Regular Customer" if completed_count >= 10 else "Casual User"

            print(f"{user.username:<20} {total_bookings:<12} {user.bonus_points:<15} {user_type}")

        print("="*70)

        # Show regular customers count
        regular_customers = [u for u in users if u.bonus_points >= 100]  # Approximation
        print(f"\nTotal Users: {len(users)}")
        print(f"Regular Customers (10+ completed bookings): ~{len(regular_customers)}")


async def main():
    """Main execution function."""
    print("\n" + "="*70)
    print("ADDING MORE USERS WITH VARYING BOOKING DATA")
    print("="*70 + "\n")

    print("Step 1: Creating additional users...")
    users_with_booking_count = await create_additional_users()

    if not users_with_booking_count:
        print("\n[INFO] No new users were created. All users might already exist.")
        await show_summary()
        return

    print("\nStep 2: Creating bookings for new users...")
    await create_bookings_for_users(users_with_booking_count)

    print("\nStep 3: Generating summary...")
    await show_summary()

    print("\n[SUCCESS] Database populated with additional users!")
    print("\nLogin credentials for all new users:")
    print("  Password: User123!")
    print("\nRegular Customers (10+ completed bookings):")
    print("  - sarah_johnson")
    print("  - mike_brown")
    print("  - emma_davis")
    print("\nCasual Users:")
    print("  - alex_martinez (5 bookings)")
    print("  - lisa_anderson (3 bookings)")
    print("  - tom_wilson (2 bookings)")
    print("  - rachel_lee (1 booking)")


if __name__ == "__main__":
    asyncio.run(main())
