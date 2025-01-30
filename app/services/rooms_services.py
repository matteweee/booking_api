from datetime import date

from sqlalchemy import and_, func, or_, select

from app.database.database import async_session_maker
from app.database.models.bookings_models import Bookings
from app.database.models.rooms_models import Rooms
from app.schemas.rooms_schemas import SRoom, SRoomsLeft
from app.services.base import BaseService


class RoomService(BaseService):
    model = Rooms

    @classmethod
    async def rooms_left(
        cls,
        room_id: int,
        date_from: date,
        date_to: date,
    ) -> int:
        async with async_session_maker() as sess:
            book_rooms = (
                select(Bookings)
                .where(
                    and_(
                        Bookings.room_id == room_id,
                        or_(
                            and_(
                                Bookings.date_from >= date_from,
                                Bookings.date_from <= date_to,
                            ),
                            and_(
                                Bookings.date_from <= date_from,
                                Bookings.date_to > date_from,
                            ),
                        ),
                    )
                )
                .cte("book_rooms")
            )

            get_rooms_le = (
                select(Rooms.quantity - func.count(book_rooms.c.room_id))
                .select_from(Rooms)
                .join(book_rooms, book_rooms.c.room_id == Rooms.id, isouter=True)
                .where(Rooms.id == room_id)
                .group_by(Rooms.quantity, book_rooms.c.room_id)
            )

            # print(get_rooms_le.compile(engine, compile_kwargs={"literal_binds": True}))

            # rooms_left = await sess.execute(get_rooms_left)
            # rooms_left: int = rooms_left.scalar()
            rooms_left = await sess.scalar(get_rooms_le)
            return rooms_left

    @classmethod
    async def get_rooms(
        cls,
        hotel_id: int,
        date_from: date,
        date_to: date,
    ):

        get_rooms: list[Rooms] = await RoomService.find_all(hotel_id=hotel_id)
        rooms: SRoomsLeft = []
        for room in get_rooms:
            count_room: int = await RoomService.rooms_left(room.id, date_from, date_to)
            rooms.append(
                SRoomsLeft(
                    room=SRoom(
                        id=room.id,
                        hotel_id=room.hotel_id,
                        name=room.name,
                        description=room.description,
                        price=room.price,
                        services=room.services,
                        quantity=room.quantity,
                        image_id=room.image_id,
                    ),
                    rooms_left=count_room,
                )
            )
        return rooms
