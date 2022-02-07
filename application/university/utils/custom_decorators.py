import uuid
from functools import wraps

from flask_jwt_extended import get_jwt_identity

from application import UserModel, PositionModel
from application.university.utils.constants import (
    NOT_FOUND_BY_ID,
    NOT_ACTIVE_USER,
    ALREADY_EXISTS,
    PW_DO_NOT_MATCH,
    ALREADY_EXISTS_WITH_YEAR,
    POSITION,
    DOES_NOT_EXIST,
    STUDENT,
    PERMISSION_DENIED,
)
from application.university.utils.custom_exceptions import (
    SearchException,
    CreateException,
)
from application.university.utils.utils import get_hashed_password


def find_active_user(specific_model, user_type, *, check_jwt=False):
    def decorator(func):
        @wraps(func)
        def wrapper(**kwargs):
            if user_type == STUDENT:
                user_id = kwargs.pop("student_id")
            else:
                user_id = kwargs.pop("teacher_id")
            specific_user = specific_model.get_by_id(user_id)
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


def process_user_json(user_schema, user_type, request):
    def decorator(func):
        @wraps(func)
        def wrapper():
            user_json = request.get_json()
            user = user_schema.load(user_json)
            user_obj = UserModel.get_by_email(user_json.get("email", None))
            if user_obj:
                raise CreateException(
                    ALREADY_EXISTS.format(user_type, user_obj.email)
                )
            if user_json["password"] != user_json.get("password1", None):
                raise CreateException(PW_DO_NOT_MATCH)
            else:
                position_id = request.get_json().get("position_id", None)
                if position_id:
                    position = PositionModel.get_by_id(position_id)
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


def create_obj_with_name_and_year(model, model_type, schema, request):
    def decorator(func):
        @wraps(func)
        def wrapper():
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
            return func(schema_obj, requested_json)

        return wrapper

    return decorator
