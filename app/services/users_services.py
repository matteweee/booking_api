from app.database.models.users_models import Users
from app.services.base import BaseService


class UserService(BaseService):
    model = Users
