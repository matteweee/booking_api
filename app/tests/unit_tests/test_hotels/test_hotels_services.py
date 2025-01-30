import pytest

from app.services.hotels_services import HotelService


@pytest.mark.parametrize(
    "hotel_id, exists",
    [
        (1, True),
        (6, True),
        (7, False),
    ],
)
async def test_find_user_by_id(hotel_id, exists):
    hotel = await HotelService.find_one_or_none(id=hotel_id)

    if exists:
        assert hotel
        assert hotel.id == hotel_id
    else:
        assert not hotel
