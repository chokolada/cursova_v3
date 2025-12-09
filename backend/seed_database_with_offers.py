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

        bookings_data = [
            {
                "user": users[0],
                "room": rooms[0],
                "check_in": now - timedelta(days=10),
                "check_out": now - timedelta(days=7),
                "guests": 1,
                "status": BookingStatus.COMPLETED,
                "special_requests": "Please provide extra towels.",
                "offers": [breakfast] if breakfast else []
            },
            {
                "user": users[1],
                "room": rooms[3],
                "check_in": now - timedelta(days=5),
                "check_out": now + timedelta(days=2),
                "guests": 2,
                "status": BookingStatus.CONFIRMED,
                "special_requests": "Anniversary celebration - could you arrange flowers in the room?",
                "offers": [breakfast, dinner] if breakfast and dinner else []
            },
            {
                "user": users[0],
                "room": rooms[5],
                "check_in": now + timedelta(days=7),
                "check_out": now + timedelta(days=10),
                "guests": 3,
                "status": BookingStatus.PENDING,
                "special_requests": "Family with young child. Need a crib if available.",
                "offers": [breakfast, massage] if breakfast and massage else []
            },
            {
                "user": users[2],
                "room": rooms[7],
                "check_in": now + timedelta(days=14),
                "check_out": now + timedelta(days=17),
                "guests": 2,
                "status": BookingStatus.CONFIRMED,
                "special_requests": "Honeymoon suite. Looking forward to the premium experience!",
                "offers": [breakfast, dinner, massage, alcohol] if all([breakfast, dinner, massage, alcohol]) else []
            },
            {
                "user": users[1],
                "room": rooms[2],
                "check_in": now - timedelta(days=3),
                "check_out": now + timedelta(days=4),
                "guests": 2,
                "status": BookingStatus.CONFIRMED,
                "special_requests": None,
                "offers": []
            },
            {
                "user": users[2],
                "room": rooms[4],
                "check_in": now + timedelta(days=20),
                "check_out": now + timedelta(days=23),
                "guests": 2,
                "status": BookingStatus.PENDING,
                "special_requests": "Business trip. Need stable WiFi and quiet room for conference calls.",
                "offers": [breakfast] if breakfast else []
            },
            {
                "user": users[0],
                "room": rooms[1],
                "check_in": now + timedelta(days=5),
                "check_out": now + timedelta(days=7),
                "guests": 1,
                "status": BookingStatus.CANCELLED,
                "special_requests": "Unfortunately need to cancel due to schedule change.",
                "offers": []
            },
            {
                "user": users[1],
                "room": rooms[9],
                "check_in": now + timedelta(days=30),
                "check_out": now + timedelta(days=35),
                "guests": 2,
                "status": BookingStatus.PENDING,
                "special_requests": "Special occasion - 10th wedding anniversary. Would love champagne and roses package!",
                "offers": [breakfast, dinner, massage] if all([breakfast, dinner, massage]) else []
            }
        ]

        for booking_data in bookings_data:
            user = booking_data["user"]
            room = booking_data["room"]
            check_in = booking_data["check_in"]
            check_out = booking_data["check_out"]
            guests = booking_data["guests"]
            status = booking_data["status"]
            special_requests = booking_data["special_requests"]
            selected_offers = booking_data["offers"]

            # Calculate total price
            nights = (check_out - check_in).days
            room_price = room.price_per_night * nights
            offers_price = sum(offer.price for offer in selected_offers)
            total_price = room_price + offers_price

            booking = Booking(
                user_id=user.id,
                room_id=room.id,
                check_in_date=check_in,
                check_out_date=check_out,
                guests_count=guests,
                total_price=total_price,
                status=status,
                special_requests=special_requests
            )
            booking.selected_offers = selected_offers
            session.add(booking)

        await session.commit()
        print(f"[OK] Created {len(bookings_data)} bookings with offer selections")


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
