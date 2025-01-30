from datetime import datetime

import pytest

from app.services.bookings_services import BookingService


@pytest.mark.parametrize(
    "user_id, room_id, date_from, date_to",
    [
        (2, 2, "2024-12-05", "2024-12-20"),
        (2, 3, "2024-12-05", "2024-12-20"),
        (1, 4, "2024-12-05", "2024-12-20"),
        (1, 4, "2024-12-05", "2024-12-20"),
    ],
)
async def test_booking_crud(user_id, room_id, date_from, date_to):
    new_booking = await BookingService.add(
        user_id=user_id,
        room_id=room_id,
        date_from=datetime.strptime(date_from, "%Y-%m-%d"),
        date_to=datetime.strptime(date_to, "%Y-%m-%d"),
    )

    assert new_booking.user_id == user_id
    assert new_booking.room_id == room_id

    new_booking = await BookingService.find_by_id(new_booking.id)
    assert new_booking

    await BookingService.delete(
        booking_id=new_booking.id,
        user_id=user_id,
    )

    deleted_booking = await BookingService.find_one_or_none(id=new_booking.id)
    assert not deleted_booking
