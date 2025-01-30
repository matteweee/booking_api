from datetime import date

from sqlalchemy import and_, insert, select
from sqlalchemy.exc import SQLAlchemyError

from app.database.database import async_session_maker
from app.database.models.bookings_models import Bookings
from app.database.models.rooms_models import Rooms
from app.logger import logger
from app.services.base import BaseService
from app.services.rooms_services import RoomService


class BookingService(BaseService):
    model = Bookings

    @classmethod
    async def add(cls, user_id: int, room_id: int, date_from: date, date_to: date):
        try:
            async with async_session_maker() as session:
                rooms_left = await RoomService.rooms_left(room_id, date_from, date_to)

                if rooms_left > 0:
                    get_price = select(Rooms.price).filter_by(id=room_id)
                    price = await session.execute(get_price)
                    price: int = price.scalar()
                    add_booking = (
                        insert(Bookings)
                        .values(
                            room_id=room_id,
                            user_id=user_id,
                            date_from=date_from,
                            date_to=date_to,
                            price=price,
                        )
                        .returning(Bookings)
                    )

                    new_booking = await session.execute(add_booking)
                    await session.commit()
                    return new_booking.scalar()
                else:
                    return None
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            elif isinstance(e, Exception):
                msg = "Unknown Exc"
            msg += ": Cannot add booking"
            extra = {
                "user_id": user_id,
                "room_id": room_id,
                "date_from": date_from,
                "date_to": date_to,
            }
            logger.error(msg, extra=extra, exc_info=True)

    @classmethod
    async def find_all(cls, user_id: int):
        async with async_session_maker() as session:
            bookings = select(Bookings).where(Bookings.user_id == user_id)
            bookings = await session.execute(bookings)
            bookings = bookings.scalars().all()

            list_bookings = []
            for booking in bookings:
                temp_room = await RoomService.find_by_id(booking.room_id)
                list_bookings.append(
                    {
                        "id": booking.id,
                        "room_id": booking.room_id,
                        "user_id": booking.user_id,
                        "date_from": booking.date_from,
                        "date_to": booking.date_to,
                        "price": booking.price,
                        "total_cost": booking.total_cost,
                        "total_days": booking.total_days,
                        "image_id": temp_room.image_id,
                        "name": temp_room.name,
                        "description": temp_room.description,
                        "services": temp_room.services,
                    }
                )

            return list_bookings

    @classmethod
    async def delete(cls, booking_id: int, user_id: int):
        async with async_session_maker() as session:
            delete_booking = select(Bookings).where(
                and_(
                    Bookings.id == booking_id,
                    Bookings.user_id == user_id,
                )
            )
            booking = await session.execute(delete_booking)
            booking = booking.scalar_one()
            await session.delete(booking)
            await session.commit()
            return booking
