from functools import wraps

from positions import models as position_models
from users import models as user_models
from utils.constants import (
    ALREADY_EXISTS,
    PW_DO_NOT_MATCH,
    DOES_NOT_EXIST,
    POSITION,
)
from utils.custom_exceptions import CreateException, SearchException
from utils.utils import get_hashed_password


def process_user_json(user_schema, user_type, request):
    def decorator(func):
        @wraps(func)
        def wrapper():
            user_json = request.get_json()
            user = user_schema.load(user_json)
            user_obj = user_models.UserModel.get_by_email(
                user_json.get("email", None)
            )
            if user_obj:
                raise CreateException(
                    ALREADY_EXISTS.format(user_type, user_obj.email)
                )
            if user_json["password"] != user_json.get("password1", None):
                raise CreateException(PW_DO_NOT_MATCH)
            position_id = request.get_json().get("position_id", None)
            if position_id:
                position = position_models.PositionModel.get_by_id(position_id)
                if not position:
                    raise SearchException(
                        DOES_NOT_EXIST.format(POSITION, position_id),
                        status_code=400,
                    )
            user.password = get_hashed_password(
                user.password.encode("utf8")
            ).decode("utf-8")
            user.save_to_db()
            return func(user)

        return wrapper

    return decorator
