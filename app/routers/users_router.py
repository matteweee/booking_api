from fastapi import APIRouter, Depends, Response

from app.config.auth import authentitace_user, create_access_token, get_password_hash
from app.database.models.users_models import Users
from app.dependencies.dependencies import get_current_admin, get_current_user
from app.exceptions import IncorrectEmailOrPasswordException, UserAlreadyExistsException
from app.schemas.users_schemas import SToken, SUser, SUserAuth
from app.services.users_services import UserService

router = APIRouter(
    prefix="/auth",
    tags=["Auth & Users"],
)


@router.post("/register")
async def register_user(user_data: SUserAuth):
    existing_user = await UserService.find_one_or_none(email=user_data.email)
    if existing_user:
        raise UserAlreadyExistsException()
    hashed_password = get_password_hash(user_data.password)
    await UserService.add(email=user_data.email, hashed_password=hashed_password)
    # return await UserService.find_one_or_none(email=user_data.email)


@router.post("/login")
async def login_user(response: Response, user_data: SUserAuth) -> SToken:
    user = await authentitace_user(email=user_data.email, password=user_data.password)
    if not user:
        raise IncorrectEmailOrPasswordException()
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie("booking_access_token", access_token, httponly=True)
    return {"access_token": access_token}


@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie("booking_access_token")


@router.get("/me")
async def read_users_me(current_user: Users = Depends(get_current_user)) -> SUser:
    return current_user


@router.get("/all")
async def read_users_all(
    current_user: Users = Depends(get_current_admin),
) -> list[SUser]:
    return await UserService.find_all()
