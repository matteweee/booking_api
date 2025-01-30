from fastapi import HTTPException, status


class BookingException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(
            status_code=self.status_code,
            detail=self.detail,
        )


class HotelException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(
            status_code=self.status_code,
            detail=self.detail,
        )


class UserAlreadyExistsException(BookingException):

    status_code = status.HTTP_409_CONFLICT
    detail = "User already exists"


class IncorrectEmailOrPasswordException(BookingException):

    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Incorrect email or password"


class TokenExpiredException(BookingException):

    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Token expired"


class TokenAbsentException(BookingException):

    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Token absent"


class IncorrectTokenFormatException(BookingException):

    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Incorrect token format"


class UserIsNotPresentException(BookingException):

    status_code = status.HTTP_401_UNAUTHORIZED


class RoomCannotBeBookedException(BookingException):

    status_code = status.HTTP_409_CONFLICT
    detail = "Room cannot be booked"


class DateFromCannotBeAfterDateTo(HotelException):

    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Incorrent chosen dates"


class CannotBookHotelForLongPeriod(HotelException):

    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Cannot book hotel for period more than 31 days"
