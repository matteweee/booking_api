import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "room_id, date_from, date_to, booked_rooms, status_code",
    [
        (4, "2030-05-15", "2030-05-25", 7, 200),
        (4, "2030-05-15", "2030-05-25", 8, 200),
        (4, "2030-05-15", "2030-05-25", 9, 200),
        (4, "2030-05-15", "2030-05-25", 10, 200),
        (4, "2030-05-15", "2030-05-25", 11, 200),
        (4, "2030-05-15", "2030-05-25", 12, 200),
        (4, "2030-05-15", "2030-05-25", 13, 200),
        (4, "2030-05-15", "2030-05-25", 14, 200),
        (4, "2030-05-15", "2030-05-25", 14, 409),
        (4, "2030-05-15", "2030-05-25", 14, 409),
    ],
)
async def test_add_and_get_booking(
    room_id,
    date_from,
    date_to,
    booked_rooms,
    status_code,
    authenticated_ac: AsyncClient,
):
    response = await authenticated_ac.post(
        "/bookings",
        params={
            "room_id": room_id,
            "date_from": date_from,
            "date_to": date_to,
        },
    )

    assert response.status_code == status_code

    response = await authenticated_ac.get("/bookings")

    assert len(response.json()) == booked_rooms


async def test_get_and_delete_booking(authenticated_ac: AsyncClient):
    response = await authenticated_ac.get("/bookings")
    existing_bookings = [booking["id"] for booking in response.json()]
    for booking_id in existing_bookings:
        response = await authenticated_ac.delete(
            f"/bookings/{booking_id}",
        )

    response = await authenticated_ac.get("/bookings")
    assert len(response.json()) == 0
