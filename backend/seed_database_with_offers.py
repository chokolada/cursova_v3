"""
Comprehensive database seeding script with offers system.
Creates users, rooms, offers, and bookings with offer selections.
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select, text
from app.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.room import Room
from app.models.booking import Booking, BookingStatus
from app.models.offer import Offer, OfferType
from app.core.security import get_password_hash


async def clear_database():
    """Clear all data except admin users."""
    async with AsyncSessionLocal() as session:
        # Clear in order of dependencies
        await session.execute(text("DELETE FROM booking_offers"))
        await session.execute(text("DELETE FROM room_offers"))
        await session.execute(text("DELETE FROM bookings"))
        await session.execute(text("DELETE FROM offers"))
        await session.execute(text("DELETE FROM rooms"))
        await session.execute(text("DELETE FROM users WHERE role != 'admin'"))
        await session.commit()
    print("[OK] Database cleared (kept admin users)")


async def create_users():
    """Create test users."""
    async with AsyncSessionLocal() as session:
        users_data = [
            {
                "username": "manager1",
                "email": "manager1@hotel.com",
                "password": "Manager123!",
                "full_name": "Hotel Manager",
                "role": UserRole.MANAGER
            },
            {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "User123!",
                "full_name": "John Doe",
                "role": UserRole.USER
            },
            {
                "username": "jane_smith",
                "email": "jane@example.com",
                "password": "User123!",
                "full_name": "Jane Smith",
                "role": UserRole.USER
            },
            {
                "username": "bob_wilson",
                "email": "bob@example.com",
                "password": "User123!",
                "full_name": "Bob Wilson",
                "role": UserRole.USER
            }
        ]

        created_users = []
        for user_data in users_data:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                full_name=user_data["full_name"],
                role=user_data["role"],
                is_active=True
            )
            session.add(user)
            created_users.append(user_data["username"])

        await session.commit()
        print(f"[OK] Created {len(created_users)} users: {', '.join(created_users)}")


async def create_offers():
    """Create special offers."""
    async with AsyncSessionLocal() as session:
        offers_data = [
            # Global offers (available for all rooms)
            {
                "name": "Breakfast",
                "description": "Delicious continental breakfast buffet",
                "price": 15.0,
                "offer_type": OfferType.GLOBAL
            },
            {
                "name": "Lunch",
                "description": "Three-course lunch menu",
                "price": 25.0,
                "offer_type": OfferType.GLOBAL
            },
            {
                "name": "Dinner",
                "description": "Gourmet dinner experience",
                "price": 40.0,
                "offer_type": OfferType.GLOBAL
            },
            {
                "name": "Spa Massage",
                "description": "60-minute relaxing massage",
                "price": 80.0,
                "offer_type": OfferType.GLOBAL
            },
            {
                "name": "Airport Transfer",
                "description": "Private airport pickup/dropoff",
                "price": 50.0,
                "offer_type": OfferType.GLOBAL
            },
            {
                "name": "Late Checkout",
                "description": "Checkout at 2 PM instead of 11 AM",
                "price": 30.0,
                "offer_type": OfferType.GLOBAL
            },

            # Room-specific offers (for deluxe/suite rooms)
            {
                "name": "Premium Alcohol Package",
                "description": "Selection of premium wines and spirits in your room",
                "price": 120.0,
                "offer_type": OfferType.ROOM_SPECIFIC
            },
            {
                "name": "Private Chef Service",
                "description": "Personal chef for in-room dining experience",
                "price": 200.0,
                "offer_type": OfferType.ROOM_SPECIFIC
            },
            {
                "name": "Champagne & Roses",
                "description": "Bottle of champagne with fresh roses",
                "price": 75.0,
                "offer_type": OfferType.ROOM_SPECIFIC
            },
            {
                "name": "Butler Service",
                "description": "24-hour personal butler service",
                "price": 150.0,
                "offer_type": OfferType.ROOM_SPECIFIC
            }
        ]

        created_offers = []
        for offer_data in offers_data:
            offer = Offer(**offer_data, is_active=True)
            session.add(offer)
            created_offers.append(offer_data["name"])

        await session.commit()
        print(f"[OK] Created {len(created_offers)} offers")
        return created_offers


async def create_rooms():
    """Create hotel rooms with offer assignments."""
    async with AsyncSessionLocal() as session:
        # Get all offers
        result = await session.execute(select(Offer))
        all_offers = list(result.scalars().all())

        global_offers = [o for o in all_offers if o.offer_type == OfferType.GLOBAL]
        specific_offers = [o for o in all_offers if o.offer_type == OfferType.ROOM_SPECIFIC]

        rooms_data = [
            # Single rooms
            {
                "room_number": "101",
                "room_type": "single",
                "price_per_night": 80.0,
                "capacity": 1,
                "floor": 1,
                "description": "Cozy single room with city view",
                "amenities": "Free WiFi, TV, Mini-fridge, Air conditioning",
                "offers": global_offers  # Only global offers
            },
            {
                "room_number": "102",
                "room_type": "single",
                "price_per_night": 85.0,
                "capacity": 1,
                "floor": 1,
                "description": "Modern single room with work desk",
                "amenities": "Free WiFi, TV, Work desk, Coffee maker",
                "offers": global_offers
            },

            # Double rooms
            {
                "room_number": "201",
                "room_type": "double",
                "price_per_night": 120.0,
                "capacity": 2,
                "floor": 2,
                "description": "Spacious double room with queen bed",
                "amenities": "Free WiFi, TV, Mini-bar, Balcony, Air conditioning",
                "offers": global_offers
            },
            {
                "room_number": "202",
                "room_type": "double",
                "price_per_night": 130.0,
                "capacity": 2,
                "floor": 2,
                "description": "Luxury double room with sea view",
                "amenities": "Free WiFi, Smart TV, Mini-bar, Balcony, Bathtub",
                "offers": global_offers
            },
            {
                "room_number": "203",
                "room_type": "double",
                "price_per_night": 125.0,
                "capacity": 2,
                "floor": 2,
                "description": "Elegant double room with modern amenities",
                "amenities": "Free WiFi, TV, Mini-bar, Work desk, Safe",
                "offers": global_offers
            },

            # Suite rooms (with special offers)
            {
                "room_number": "301",
                "room_type": "suite",
                "price_per_night": 200.0,
                "capacity": 3,
                "floor": 3,
                "description": "Executive suite with living room and bedroom",
                "amenities": "Free WiFi, Smart TV, Mini-bar, Jacuzzi, Kitchen, Dining area",
                "offers": global_offers + specific_offers[:2]  # Add some special offers
            },
            {
                "room_number": "302",
                "room_type": "suite",
                "price_per_night": 220.0,
                "capacity": 4,
                "floor": 3,
                "description": "Family suite with two bedrooms",
                "amenities": "Free WiFi, 2 TVs, Full kitchen, Washing machine, Balcony",
                "offers": global_offers + specific_offers[:2]
            },

            # Deluxe rooms (with all special offers)
            {
                "room_number": "401",
                "room_type": "deluxe",
                "price_per_night": 300.0,
                "capacity": 2,
                "floor": 4,
                "description": "Premium deluxe room with panoramic views",
                "amenities": "Free WiFi, Smart TV, Premium mini-bar, Jacuzzi, Walk-in closet, Terrace",
                "offers": global_offers + specific_offers  # All offers available
            },
            {
                "room_number": "402",
                "room_type": "deluxe",
                "price_per_night": 320.0,
                "capacity": 2,
                "floor": 4,
                "description": "Luxury deluxe suite with private spa",
                "amenities": "Free WiFi, Smart TV, Premium bar, Private sauna, Steam room, Terrace",
                "offers": global_offers + specific_offers  # All offers available
            },
            {
                "room_number": "403",
                "room_type": "deluxe",
                "price_per_night": 350.0,
                "capacity": 3,
                "floor": 4,
                "description": "Presidential deluxe suite",
                "amenities": "Free WiFi, Home theater, Full bar, Private gym, Piano, Panoramic terrace",
                "offers": global_offers + specific_offers  # All offers available
            }
        ]

        created_rooms = []
        for room_data in rooms_data:
            offers = room_data.pop("offers")
            room = Room(**room_data, is_available=True)
            room.available_offers = offers
            session.add(room)
            created_rooms.append(room_data["room_number"])

        await session.commit()
        print(f"[OK] Created {len(created_rooms)} rooms: {', '.join(created_rooms)}")


async def create_bookings():
    """Create sample bookings with offer selections."""
    async with AsyncSessionLocal() as session:
        # Get users and rooms
        users_result = await session.execute(
            select(User).where(User.role == UserRole.USER)
        )
        users = list(users_result.scalars().all())

        rooms_result = await session.execute(select(Room))
        rooms = list(rooms_result.scalars().all())

        offers_result = await session.execute(select(Offer))
        all_offers = list(offers_result.scalars().all())

        breakfast = next((o for o in all_offers if o.name == "Breakfast"), None)
        dinner = next((o for o in all_offers if o.name == "Dinner"), None)
        massage = next((o for o in all_offers if o.name == "Spa Massage"), None)
        alcohol = next((o for o in all_offers if o.name == "Premium Alcohol Package"), None)

        now = datetime.utcnow()
        current_month_start = now.replace(day=1)
        prev_month_start = (current_month_start - timedelta(days=1)).replace(day=1)  # last month
        prev2_month_start = (prev_month_start - timedelta(days=1)).replace(day=1)   # two months ago

        def add_booking(user, room, start_offset, nights, status, offers=None, special_requests=None, guests=None):
            check_in = now + timedelta(days=start_offset)
            check_out = check_in + timedelta(days=nights)
            selected_offers = offers or []
            nights_count = (check_out - check_in).days
            room_price = room.price_per_night * nights_count
            offers_price = sum(o.price for o in selected_offers)
            total_price = room_price + offers_price

            booking = Booking(
                user_id=user.id,
                room_id=room.id,
                check_in_date=check_in,
                check_out_date=check_out,
                guests_count=guests or room.capacity,
                total_price=total_price,
                status=status,
                special_requests=special_requests
            )
            booking.selected_offers = selected_offers
            session.add(booking)

        # Generate bookings spread over the last 60 days and next 30 days
        add_booking(users[0], rooms[0], start_offset=-55, nights=3, status=BookingStatus.COMPLETED, offers=[breakfast], special_requests="Early check-in if possible", guests=1)
        add_booking(users[1], rooms[1], start_offset=-48, nights=4, status=BookingStatus.COMPLETED, offers=[breakfast, dinner], guests=1)
        add_booking(users[2], rooms[2], start_offset=-42, nights=5, status=BookingStatus.COMPLETED, offers=[breakfast], guests=2)
        add_booking(users[0], rooms[3], start_offset=-35, nights=3, status=BookingStatus.COMPLETED, offers=[massage], guests=2)
        add_booking(users[1], rooms[4], start_offset=-30, nights=6, status=BookingStatus.COMPLETED, offers=[breakfast, dinner], guests=2)
        add_booking(users[2], rooms[5], start_offset=-24, nights=3, status=BookingStatus.COMPLETED, offers=[breakfast], guests=3)
        add_booking(users[0], rooms[6], start_offset=-18, nights=4, status=BookingStatus.CONFIRMED, offers=[breakfast, dinner, massage], guests=2, special_requests="Birthday trip")
        add_booking(users[1], rooms[7], start_offset=-15, nights=3, status=BookingStatus.CONFIRMED, offers=[breakfast, alcohol], guests=2, special_requests="Anniversary - flowers on arrival")
        add_booking(users[2], rooms[8], start_offset=-12, nights=2, status=BookingStatus.CONFIRMED, offers=[breakfast], guests=2)
        add_booking(users[0], rooms[9], start_offset=-8, nights=5, status=BookingStatus.CONFIRMED, offers=[breakfast, dinner, massage, alcohol], guests=2)

        # Recent/ongoing
        add_booking(users[1], rooms[0], start_offset=-5, nights=4, status=BookingStatus.CONFIRMED, offers=[breakfast], guests=1)
        add_booking(users[2], rooms[1], start_offset=-3, nights=3, status=BookingStatus.CONFIRMED, offers=[breakfast], guests=2)

        # Upcoming within next month
        add_booking(users[0], rooms[2], start_offset=2, nights=3, status=BookingStatus.PENDING, offers=[breakfast], guests=2)
        add_booking(users[1], rooms[3], start_offset=5, nights=4, status=BookingStatus.PENDING, offers=[breakfast, dinner], guests=2)
        add_booking(users[2], rooms[4], start_offset=9, nights=3, status=BookingStatus.PENDING, offers=[massage], guests=2)
        add_booking(users[0], rooms[5], start_offset=12, nights=5, status=BookingStatus.PENDING, offers=[breakfast, dinner], guests=3)
        add_booking(users[1], rooms[6], start_offset=15, nights=3, status=BookingStatus.CONFIRMED, offers=[breakfast, alcohol], guests=2)
        add_booking(users[2], rooms[7], start_offset=20, nights=4, status=BookingStatus.PENDING, offers=[breakfast, massage], guests=2)
        add_booking(users[0], rooms[8], start_offset=24, nights=3, status=BookingStatus.PENDING, offers=[breakfast], guests=2)
        add_booking(users[1], rooms[9], start_offset=28, nights=4, status=BookingStatus.PENDING, offers=[breakfast, dinner, massage], guests=2)

        # Additional coverage for previous months (October & November)
        def offset_from_date(target_date):
            return (target_date - now).days

        # October (two months ago)
        add_booking(users[0], rooms[2], start_offset=offset_from_date(prev2_month_start + timedelta(days=2)), nights=3, status=BookingStatus.COMPLETED, offers=[breakfast], guests=2)
        add_booking(users[1], rooms[5], start_offset=offset_from_date(prev2_month_start + timedelta(days=10)), nights=4, status=BookingStatus.COMPLETED, offers=[breakfast, dinner], guests=2)
        add_booking(users[2], rooms[8], start_offset=offset_from_date(prev2_month_start + timedelta(days=20)), nights=3, status=BookingStatus.COMPLETED, offers=[massage], guests=2)

        # November (previous month)
        add_booking(users[0], rooms[3], start_offset=offset_from_date(prev_month_start + timedelta(days=3)), nights=3, status=BookingStatus.COMPLETED, offers=[breakfast], guests=2)
        add_booking(users[1], rooms[6], start_offset=offset_from_date(prev_month_start + timedelta(days=12)), nights=4, status=BookingStatus.CONFIRMED, offers=[breakfast, dinner], guests=2)
        add_booking(users[2], rooms[9], start_offset=offset_from_date(prev_month_start + timedelta(days=22)), nights=5, status=BookingStatus.CONFIRMED, offers=[breakfast, massage], guests=2)

        await session.commit()
        print("[OK] Created seed bookings with dense 2-month history and upcoming stays")


async def main():
    """Main seeding function."""
    print("\n>> Starting database seeding with offers system...")
    print("=" * 60)

    await clear_database()
    await create_users()
    await create_offers()
    await create_rooms()
    await create_bookings()

    print("=" * 60)
    print(">> Database seeding completed successfully!\n")
    print(">> Summary:")
    print("   - Admin user: Maks (maksymbornak@gmail.com / Pass123!)")
    print("   - Manager: manager1 (Manager123!)")
    print("   - Users: john_doe, jane_smith, bob_wilson (User123!)")
    print("   - Rooms: 10 rooms (single, double, suite, deluxe)")
    print("   - Offers: 10 special offers (6 global, 4 room-specific)")
    print("   - Deluxe rooms have access to premium offers like alcohol")
    print("   - Bookings: 8 sample bookings with various offer selections\n")


if __name__ == "__main__":
    asyncio.run(main())
