from datetime import date

import pydantic
from fastapi import APIRouter, Depends, status

from app.database.models.users_models import Users
from app.dependencies.dependencies import get_current_user
from app.exceptions import RoomCannotBeBookedException
from app.schemas.bookings_schemas import SBooking
from app.services.bookings_services import BookingService
from app.tasks.tasks import send_booking_confirmation_email

router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"],
)


@router.get("")
async def get_bookings(user: Users = Depends(get_current_user)):  # -> list[SBooking]:
    return await BookingService.find_all(user_id=user.id)


@router.post("", response_model=SBooking)
async def add_booking(
    room_id: int,
    date_from: date,
    date_to: date,
    user: Users = Depends(get_current_user),
):
    booking = await BookingService.add(user.id, room_id, date_from, date_to)
    if not booking:
        raise RoomCannotBeBookedException()
    booking_dict = pydantic.TypeAdapter(SBooking).validate_python(booking).model_dump()
    # send_booking_confirmation_email.delay(booking_dict, user.email) # not work in 2025
    return booking


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(booking_id: int, user: Users = Depends(get_current_user)):
    await BookingService.delete(booking_id, user.id)
