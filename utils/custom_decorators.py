import uuid
from functools import wraps

from flask_jwt_extended import get_jwt_identity

from users import models as user_models
from utils.constants import (
    NOT_FOUND_BY_ID,
    NOT_ACTIVE_USER,
    ALREADY_EXISTS_WITH_YEAR,
    STUDENT,
    PERMISSION_DENIED,
)
from utils.custom_exceptions import (
    SearchException,
    CreateException,
)


def find_active_user(user_type, *, check_jwt=False):
    def decorator(func):
        @wraps(func)
        def wrapper(**kwargs):
            if user_type == STUDENT:
                user_id = kwargs.pop("student_id")
            else:
                user_id = kwargs.pop("teacher_id")
            specific_user = user_models.UserModel.get_by_id(user_id)
            if not specific_user:
                raise SearchException(
                    message=NOT_FOUND_BY_ID.format(user_type, user_id),
                    status_code=400,
                )
            if not specific_user.is_active:
                raise SearchException(
                    message=NOT_ACTIVE_USER.format(user_type, user_id),
                    status_code=403,
                )
            if check_jwt:
                current_user_id = uuid.UUID(get_jwt_identity())
                if specific_user.id != current_user_id:
                    raise PermissionError(
                        PERMISSION_DENIED.format(str(current_user_id))
                    )
            return func(specific_user, **kwargs)

        return wrapper

    return decorator


def create_obj_with_name_and_year(model, model_type, schema, request):
    def decorator(func):
        @wraps(func)
        def wrapper(*args):
            requested_json = request.get_json()
            schema_obj = schema.load(requested_json)
            obj = model.get_by_name_and_year(
                str(requested_json["name"]), int(requested_json["year"])
            )
            if obj:
                raise CreateException(
                    ALREADY_EXISTS_WITH_YEAR.format(
                        model_type, obj.name, obj.year
                    )
                )
            return func(schema_obj, requested_json, *args)

        return wrapper

    return decorator
