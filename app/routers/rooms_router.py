from datetime import date

from app.routers.hotels_router import router as router_hotels
from app.schemas.rooms_schemas import SRoomsLeft
from app.services.rooms_services import RoomService


@router_hotels.get("/{hotel_id}/rooms")
async def get_rooms(
    hotel_id: int,
    date_from: date,
    date_to: date,
) -> list[SRoomsLeft]:
    rooms = await RoomService.get_rooms(hotel_id, date_from, date_to)
    return rooms
