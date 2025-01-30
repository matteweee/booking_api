import pytest

from app.services.users_services import UserService


@pytest.mark.parametrize(
    "id, email, exists",
    [
        (1, "test1@test.com", True),
        (2, "artem@test.com", True),
        (5, "test3@test.com", False),
    ],
)
async def test_find_user_by_id(id, email, exists):
    user = await UserService.find_by_id(id)

    if exists:
        assert user
        assert user.id == id
        assert user.email == email
    else:
        assert not user
