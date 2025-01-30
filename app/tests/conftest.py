import datetime
import json
from functools import wraps
from unittest import mock

import dotenv
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import insert

from app.config.config import settings
from app.database.database import Base, async_session_maker, engine
from app.database.models.bookings_models import Bookings
from app.database.models.hotels_models import Hotels
from app.database.models.rooms_models import Rooms
from app.database.models.users_models import Users


def mock_cache(*args, **kwargs):
    def wrapper(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            return await func(*args, **kwargs)

        return inner

    return wrapper


mock.patch("fastapi_cache.decorator.cache", mock_cache).start()

from app.main import app as fastapi_app  # noqa


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    assert settings.MODE == "TEST"

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    def open_mock_json(model: str):
        with open(f"app/tests/mock_{model}.json", "r") as file:
            return json.load(file)

    hotels = open_mock_json("hotels")
    rooms = open_mock_json("rooms")
    users = open_mock_json("users")
    bookings = open_mock_json("bookings")

    for booking in bookings:
        booking["date_from"] = datetime.datetime.strptime(
            booking["date_from"], "%Y-%m-%d"
        )
        booking["date_to"] = datetime.datetime.strptime(booking["date_to"], "%Y-%m-%d")

    async with async_session_maker() as session:
        add_hotels = insert(Hotels).values(hotels)
        add_rooms = insert(Rooms).values(rooms)
        add_users = insert(Users).values(users)
        add_bookings = insert(Bookings).values(bookings)

        await session.execute(add_hotels)
        await session.execute(add_rooms)
        await session.execute(add_users)
        await session.execute(add_bookings)

        await session.commit()


# @pytest.fixture(scope="session")
# def event_loop(request):
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()


@pytest.fixture(scope="function")
async def ac():
    async with AsyncClient(app=fastapi_app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
async def authenticated_ac():
    async with AsyncClient(app=fastapi_app, base_url="http://test") as ac:
        await ac.post(
            "/auth/login",
            json={
                "email": "test1@test.com",
                "password": "test",
            },
        )
        assert ac.cookies.get("booking_access_token")
        yield ac


@pytest.fixture(scope="function")
async def session():
    async with async_session_maker() as session:
        yield session


@pytest.fixture(autouse=True)
def run_at_end_of_tests():
    dotenv.set_key(".env", "MODE", "DEV")
    yield
