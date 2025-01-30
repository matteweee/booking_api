from datetime import date

from sqlalchemy import and_, func, or_, select

from app.database.database import async_session_maker
from app.database.models.bookings_models import Bookings
from app.database.models.hotels_models import Hotels
from app.database.models.rooms_models import Rooms
from app.schemas.hotels_schemas import SHotel, SHotelInfo
from app.services.base import BaseService
from app.services.rooms_services import RoomService


class HotelService(BaseService):
    model = Hotels

    @classmethod
    async def search_hotel_by_date(
        cls,
        location: str,
        date_from: date,
        date_to: date,
    ):
        async with async_session_maker() as session:
            search_hotel = select(Hotels).where(Hotels.location.ilike(f"%{location}%"))
            hotels = await session.execute(search_hotel)
            hotels = hotels.scalars().all()

            search_rooms_of_hotels = select(Rooms).where(
                Rooms.hotel_id.in_([hotel.id for hotel in hotels])
            )
            rooms = await session.execute(search_rooms_of_hotels)
            rooms = rooms.scalars().all()

            hotels_and_rooms = {hotel.id: 0 for hotel in hotels}

            for room in rooms:
                count_room: int = await RoomService.rooms_left(
                    room.id, date_from, date_to
                )
                hotels_and_rooms[room.hotel_id] += count_room

            hotels_and_rooms_result: SHotelInfo = []
            for hotel in hotels_and_rooms:
                if hotels_and_rooms[hotel] > 0:
                    temp_hotel = await HotelService.find_by_id(hotel)

                    hotels_and_rooms_result.append(
                        SHotelInfo(
                            hotel_info=SHotel(
                                id=temp_hotel.id,
                                name=temp_hotel.name,
                                location=temp_hotel.location,
                                services=temp_hotel.services,
                                image_id=temp_hotel.image_id,
                                rooms_quantity=temp_hotel.rooms_quantity,
                            ),
                            rooms_left=hotels_and_rooms[hotel],
                        )
                    )

            return hotels_and_rooms_result

    @classmethod
    async def find_by_date_and_location(
        cls,
        location: str,
        date_from: date,
        date_to: date,
    ):
        async with async_session_maker() as session:
            search_location = (
                select(Hotels)
                .where(Hotels.location.ilike(f"%{location}%"))
                .cte("search_location")
            )

            search_rooms = (
                select(Rooms)
                .where(Rooms.hotel_id == search_location.c.id)
                .cte("search_rooms")
            )

            book_rooms = (
                select(Bookings.room_id, func.count(Bookings.room_id).label("count"))
                .select_from(Bookings)
                .filter(
                    or_(
                        and_(
                            Bookings.date_from >= date_from,
                            Bookings.date_from <= date_to,
                        ),
                        and_(
                            Bookings.date_from <= date_from,
                            Bookings.date_to > date_from,
                        ),
                        and_(
                            Bookings.date_from < date_to,
                            Bookings.date_to >= date_to,
                        ),
                    )
                )
                .join(search_rooms, search_rooms.c.id == Bookings.room_id)
                .group_by(Bookings.room_id)
                .cte("book_rooms")
            )

            booked_rooms = (
                select(Rooms.__table__, book_rooms.c.count)
                .join(book_rooms, book_rooms.c.room_id == Rooms.id)
                .cte("booked_rooms")
            )

            hotels_with_rooms = (
                select(
                    search_location,
                    booked_rooms.c.count.label("count"),
                )
                .join(
                    booked_rooms,
                    booked_rooms.c.hotel_id == search_location.c.id,
                    full=True,
                )
                .cte("hotels_with_rooms")
            )

            hotels_with_left_rooms = select(
                hotels_with_rooms.c.id,
                hotels_with_rooms.c.name,
                hotels_with_rooms.c.location,
                hotels_with_rooms.c.services,
                hotels_with_rooms.c.rooms_quantity,
                hotels_with_rooms.c.image_id,
                func.coalesce(hotels_with_rooms.c.count, 0).label("count"),
            ).cte("hotels_with_left_rooms")

            hotels_with_count_of_rooms = select(
                hotels_with_left_rooms.c.id,
                hotels_with_left_rooms.c.name,
                hotels_with_left_rooms.c.location,
                hotels_with_left_rooms.c.services,
                hotels_with_left_rooms.c.rooms_quantity,
                hotels_with_left_rooms.c.image_id,
                (
                    hotels_with_left_rooms.c.rooms_quantity
                    - hotels_with_left_rooms.c.count
                ).label("rooms_left"),
            )

            hotels = await session.execute(hotels_with_count_of_rooms)
            hotels_orm = hotels.all()
            hotels_schema = [
                SHotelInfo.model_validate(row, from_attributes=True)
                for row in hotels_orm
            ]
            return hotels_schema
