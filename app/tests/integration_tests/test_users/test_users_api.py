import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("catdoggg@dog.com", "password123", 200),
        ("catdoggg@dog.com", "password1223", 409),
        ("catdo@dog.com", "password1223", 200),
        ("catdogg", "password123", 422),
    ],
)
async def test_register_user(email, password, status_code, ac: AsyncClient):
    response = await ac.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == status_code


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("test1@test.com", "test", 200),
        ("artem@test.com", "test", 200),
        ("ghj@test.com", "dfgh", 401),
    ],
)
async def test_login_user(email, password, status_code, ac: AsyncClient):
    response = await ac.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == status_code
