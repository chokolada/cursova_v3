"""
Seed script for populating the database with initial data.

This script creates:
- Sample users (admin, manager, regular users)
- Hotel rooms of different types
- Sample bookings
"""

import asyncio
from datetime import datetime, timedelta
from passlib.context import CryptContext
from sqlalchemy import select, text

from app.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.room import Room
from app.models.booking import Booking, BookingStatus

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def clear_database():
    """Clear all data from the database."""
    async with AsyncSessionLocal() as session:
        # Delete in correct order (considering foreign keys)
        await session.execute(text("DELETE FROM bookings"))
        await session.execute(text("DELETE FROM rooms"))
        # Keep the admin user
        await session.execute(text("DELETE FROM users WHERE role != 'ADMIN'"))
        await session.commit()
        print("Database cleared (kept admin users)")


async def create_users():
    """Create sample users."""
    async with AsyncSessionLocal() as session:
        users_data = [
            {
                "username": "manager1",
                "email": "manager1@hotel.com",
                "password": "Manager123!",
                "full_name": "Hotel Manager",
                "role": UserRole.MANAGER,
            },
            {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "User123!",
                "full_name": "John Doe",
                "role": UserRole.USER,
            },
            {
                "username": "jane_smith",
                "email": "jane@example.com",
                "password": "User123!",
                "full_name": "Jane Smith",
                "role": UserRole.USER,
            },
            {
                "username": "bob_wilson",
                "email": "bob@example.com",
                "password": "User123!",
                "full_name": "Bob Wilson",
                "role": UserRole.USER,
            },
        ]

        created_users = []
        for user_data in users_data:
            # Check if user already exists
            result = await session.execute(
                select(User).where(User.username == user_data["username"])
            )
            existing_user = result.scalar_one_or_none()

            if not existing_user:
                password = user_data.pop("password")
                hashed_password = pwd_context.hash(password)

                user = User(
                    **user_data,
                    hashed_password=hashed_password,
                    is_active=True
                )
                session.add(user)
                created_users.append(user_data["username"])

        await session.commit()
        print(f"Created {len(created_users)} users: {', '.join(created_users)}")
        return created_users


async def create_rooms():
    """Create sample hotel rooms."""
    async with AsyncSessionLocal() as session:
        rooms_data = [
            # Single rooms
            {
                "room_number": "101",
                "room_type": "single",
                "price_per_night": 80.00,
                "capacity": 1,
                "description": "Cozy single room with city view",
                "amenities": "WiFi, TV, Air Conditioning, Mini Bar",
                "floor": 1,
                "is_available": True,
            },
            {
                "room_number": "102",
                "room_type": "single",
                "price_per_night": 85.00,
                "capacity": 1,
                "description": "Comfortable single room with garden view",
                "amenities": "WiFi, TV, Air Conditioning, Safe",
                "floor": 1,
                "is_available": True,
            },
            # Double rooms
            {
                "room_number": "201",
                "room_type": "double",
                "price_per_night": 120.00,
                "capacity": 2,
                "description": "Spacious double room with king-size bed",
                "amenities": "WiFi, Smart TV, Air Conditioning, Mini Bar, Coffee Machine",
                "floor": 2,
                "is_available": True,
            },
            {
                "room_number": "202",
                "room_type": "double",
                "price_per_night": 125.00,
                "capacity": 2,
                "description": "Elegant double room with balcony",
                "amenities": "WiFi, Smart TV, Air Conditioning, Mini Bar, Balcony",
                "floor": 2,
                "is_available": True,
            },
            {
                "room_number": "203",
                "room_type": "double",
                "price_per_night": 130.00,
                "capacity": 2,
                "description": "Premium double room with sea view",
                "amenities": "WiFi, Smart TV, Air Conditioning, Mini Bar, Coffee Machine, Sea View",
                "floor": 2,
                "is_available": True,
            },
            # Suite rooms
            {
                "room_number": "301",
                "room_type": "suite",
                "price_per_night": 250.00,
                "capacity": 4,
                "description": "Luxurious suite with separate living room",
                "amenities": "WiFi, Smart TV, Air Conditioning, Mini Bar, Coffee Machine, Living Room, Jacuzzi",
                "floor": 3,
                "is_available": True,
            },
            {
                "room_number": "302",
                "room_type": "suite",
                "price_per_night": 280.00,
                "capacity": 4,
                "description": "Presidential suite with panoramic view",
                "amenities": "WiFi, Smart TV, Air Conditioning, Mini Bar, Coffee Machine, Living Room, Jacuzzi, Balcony, Panoramic View",
                "floor": 3,
                "is_available": True,
            },
            # Deluxe rooms
            {
                "room_number": "401",
                "room_type": "deluxe",
                "price_per_night": 180.00,
                "capacity": 3,
                "description": "Deluxe room with extra space and premium amenities",
                "amenities": "WiFi, Smart TV, Air Conditioning, Mini Bar, Coffee Machine, Work Desk, Premium Toiletries",
                "floor": 4,
                "is_available": True,
            },
            {
                "room_number": "402",
                "room_type": "deluxe",
                "price_per_night": 190.00,
                "capacity": 3,
                "description": "Corner deluxe room with two windows",
                "amenities": "WiFi, Smart TV, Air Conditioning, Mini Bar, Coffee Machine, Work Desk, Premium Toiletries, City View",
                "floor": 4,
                "is_available": True,
            },
            {
                "room_number": "403",
                "room_type": "deluxe",
                "price_per_night": 200.00,
                "capacity": 3,
                "description": "Deluxe room with private terrace",
                "amenities": "WiFi, Smart TV, Air Conditioning, Mini Bar, Coffee Machine, Work Desk, Premium Toiletries, Private Terrace",
                "floor": 4,
                "is_available": True,
            },
        ]

        created_rooms = []
        for room_data in rooms_data:
            # Check if room already exists
            result = await session.execute(
                select(Room).where(Room.room_number == room_data["room_number"])
            )
            existing_room = result.scalar_one_or_none()

            if not existing_room:
                room = Room(**room_data)
                session.add(room)
                created_rooms.append(room_data["room_number"])

        await session.commit()
        print(f"Created {len(created_rooms)} rooms: {', '.join(created_rooms)}")
        return created_rooms


async def create_bookings():
    """Create sample bookings."""
    async with AsyncSessionLocal() as session:
        # Get users and rooms
        users_result = await session.execute(
            select(User).where(User.role == UserRole.USER)
        )
        users = list(users_result.scalars().all())

        rooms_result = await session.execute(select(Room))
        rooms = list(rooms_result.scalars().all())

        if not users or not rooms:
            print("No users or rooms found. Skipping bookings creation.")
            return

        # Create bookings
        today = datetime.utcnow()
        bookings_data = [
            # Past completed bookings
            {
                "user": users[0],
                "room": rooms[0],
                "check_in_date": today - timedelta(days=10),
                "check_out_date": today - timedelta(days=8),
                "guests_count": 1,
                "status": BookingStatus.COMPLETED,
                "special_requests": "Early check-in please",
            },
            {
                "user": users[1],
                "room": rooms[2],
                "check_in_date": today - timedelta(days=15),
                "check_out_date": today - timedelta(days=12),
                "guests_count": 2,
                "status": BookingStatus.COMPLETED,
                "special_requests": None,
            },
            # Current bookings
            {
                "user": users[0],
                "room": rooms[1],
                "check_in_date": today - timedelta(days=1),
                "check_out_date": today + timedelta(days=2),
                "guests_count": 1,
                "status": BookingStatus.CONFIRMED,
                "special_requests": "Non-smoking room",
            },
            {
                "user": users[2],
                "room": rooms[5],
                "check_in_date": today,
                "check_out_date": today + timedelta(days=4),
                "guests_count": 3,
                "status": BookingStatus.CONFIRMED,
                "special_requests": "High floor please",
            },
            # Future bookings
            {
                "user": users[1],
                "room": rooms[3],
                "check_in_date": today + timedelta(days=5),
                "check_out_date": today + timedelta(days=8),
                "guests_count": 2,
                "status": BookingStatus.PENDING,
                "special_requests": "Extra pillows",
            },
            {
                "user": users[2],
                "room": rooms[7],
                "check_in_date": today + timedelta(days=10),
                "check_out_date": today + timedelta(days=14),
                "guests_count": 2,
                "status": BookingStatus.CONFIRMED,
                "special_requests": None,
            },
            {
                "user": users[0],
                "room": rooms[6],
                "check_in_date": today + timedelta(days=20),
                "check_out_date": today + timedelta(days=25),
                "guests_count": 4,
                "status": BookingStatus.PENDING,
                "special_requests": "Anniversary package",
            },
            # Cancelled booking
            {
                "user": users[1],
                "room": rooms[4],
                "check_in_date": today + timedelta(days=7),
                "check_out_date": today + timedelta(days=9),
                "guests_count": 2,
                "status": BookingStatus.CANCELLED,
                "special_requests": None,
            },
        ]

        created_count = 0
        for booking_data in bookings_data:
            user = booking_data.pop("user")
            room = booking_data.pop("room")

            # Calculate total price
            days = (booking_data["check_out_date"] - booking_data["check_in_date"]).days
            total_price = days * room.price_per_night

            booking = Booking(
                user_id=user.id,
                room_id=room.id,
                total_price=total_price,
                **booking_data
            )
            session.add(booking)
            created_count += 1

        await session.commit()
        print(f"Created {created_count} bookings")


async def seed_database():
    """Main function to seed the database."""
    print("=" * 50)
    print("Starting database seeding...")
    print("=" * 50)

    try:
        # Clear existing data (except admin)
        await clear_database()
        print()

        # Create users
        await create_users()
        print()

        # Create rooms
        await create_rooms()
        print()

        # Create bookings
        await create_bookings()
        print()

        print("=" * 50)
        print("Database seeding completed successfully!")
        print("=" * 50)
        print("\nTest accounts:")
        print("  Manager: manager1 / Manager123!")
        print("  User 1:  john_doe / User123!")
        print("  User 2:  jane_smith / User123!")
        print("  User 3:  bob_wilson / User123!")

    except Exception as e:
        print(f"Error seeding database: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(seed_database())
