from datetime import UTC, datetime

from fastapi import Depends, Request
from jose import JWTError, jwt

from app.config.config import settings
from app.database.models.users_models import Users
from app.exceptions import (
    IncorrectTokenFormatException,
    TokenAbsentException,
    TokenExpiredException,
    UserIsNotPresentException,
)
from app.services.users_services import UserService


def get_token(request: Request):
    token = request.cookies.get("booking_access_token")
    if not token:
        raise TokenAbsentException()
    return token


async def get_current_user(token: str = Depends(get_token)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGO)
    except JWTError:
        raise IncorrectTokenFormatException()

    expire: str = payload.get("exp")
    if (not expire) or (int(expire) < datetime.now(UTC).timestamp()):
        raise TokenExpiredException()
    user_id: int = payload.get("sub")
    if not user_id:
        raise UserIsNotPresentException()
    user = await UserService.find_by_id(int(user_id))
    if not user:
        raise UserIsNotPresentException()

    return user


async def get_current_admin(current_user: Users = Depends(get_current_user)):
    # if current_user.role != "admin":
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return current_user
