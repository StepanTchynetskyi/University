import bcrypt

from application.university.models.user import commit_specific_user
from application.university.utils.constants import (
    DOES_NOT_EXIST,
    NOT_ACTIVE_USER,
    NOT_FOUND_BY_ID,
)
from application.university.utils.custom_exceptions import SearchException
from application.university.utils.process_dates import (
    check_accessibility_for_name_and_year,
)


def update_specific_user(specific_user, user_schema, specific_schema, request):
    specific_user_json = request.get_json()
    user_json = specific_user_json.pop("user", None)

    if user_json:
        user = user_schema.load(
            user_json, instance=specific_user.user, partial=True
        )
        student = specific_schema.load(
            specific_user_json, instance=specific_user, partial=True
        )
        commit_specific_user(user, student)
    else:
        student = specific_schema.load(
            specific_user_json, instance=specific_user, partial=True
        )
        student.save_to_db()
    return specific_schema.dump(student)


def is_active_user(json_, user_model, user_type):
    user_id = json_.get("teacher_id", None)
    if user_id:
        teacher = user_model.get_by_id(user_id)
        if not teacher:
            raise SearchException(
                DOES_NOT_EXIST.format(user_type, user_id), 400
            )
        if not teacher.is_active:
            raise SearchException(NOT_ACTIVE_USER.format(user_type, user_id))


def get_hashed_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())


def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(
        plain_text_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def update_obj_with_name_and_year(
    entity_info, request, *, user_model=None, user_type=None
):
    entity_obj = entity_info.model.get_by_id(entity_info.id)
    if not entity_obj:
        raise SearchException(
            NOT_FOUND_BY_ID.format(entity_info.type, entity_info.id)
        )
    entity_json = request.get_json()
    if user_model:
        is_active_user(entity_json, user_model, user_type)
    check_accessibility_for_name_and_year(
        entity_obj, entity_json, entity_info.model, entity_info.type
    )
    entity_obj = entity_info.schema.load(
        entity_json, instance=entity_obj, partial=True
    )
    entity_obj.save_to_db()
    entity_json = entity_info.schema.dump(entity_obj)
    return entity_json
