from datetime import date
from typing import List

from fastapi import APIRouter
from fastapi_cache.decorator import cache

from app.exceptions import CannotBookHotelForLongPeriod, DateFromCannotBeAfterDateTo
from app.schemas.hotels_schemas import SHotel, SHotelInfo
from app.services.hotels_services import HotelService

router = APIRouter(
    prefix="/hotels",
    tags=["Hotels"],
)


@router.get("")
def get_hotels():
    pass


@router.get("/{location}", response_model=List[SHotelInfo])
@cache(expire=20)
async def search_hotel(
    location: str,
    date_from: date,
    date_to: date,
):
    if date_from > date_to:
        raise DateFromCannotBeAfterDateTo
    if (date_to - date_from).days > 31:
        raise CannotBookHotelForLongPeriod

    hotels = await HotelService.find_by_date_and_location(location, date_from, date_to)
    return hotels


@router.get("/id/{hotel_id}")
async def get_hotel_by_id(hotel_id: int) -> SHotel | None:
    return await HotelService.find_by_id(hotel_id)
