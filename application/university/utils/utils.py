import bcrypt

from marshmallow import ValidationError

from application.university.utils.constants import (
    DOES_NOT_EXIST,
    NOT_ACTIVE_USER,
    NOT_FOUND_BY_ID,
    ITEM_NOT_PROVIDED,
    PERMISSION_DENIED,
    GROUP,
    ALREADY_EXISTS_WITH_YEAR,
)
from application.university.utils.custom_exceptions import (
    SearchException,
    NotProvided,
)


def update_specific_user(specific_user, specific_schema, request):
    specific_user_json = request.get_json()
    specific_user = specific_schema.load(
        specific_user_json, instance=specific_user, partial=True
    )
    specific_user.save_to_db()
    return specific_schema.dump(specific_user)


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


def process_many_to_many_insert(
    entity_obj, entity_schema, item_type, item_ids, item_model
):
    if not item_ids:
        raise NotProvided(ITEM_NOT_PROVIDED.format(item_type))
    items = item_model.get_by_ids(item_ids)
    if not items:
        raise SearchException(NOT_FOUND_BY_ID.format(item_type, item_ids))
    not_found_ids = [item.id for item in items if str(item.id) not in item_ids]
    if not not_found_ids:
        entity_obj.subjects.extend(items)
        entity_obj.save_to_db()
    else:
        raise SearchException(NOT_FOUND_BY_ID.format(item_type, not_found_ids))
    entity_json = entity_schema.dump(entity_obj)
    return entity_json


def process_entity_with_teacher(teacher, entity_id, entity_model, entity_type):
    entity = entity_model.get_by_id(entity_id)
    if not entity:
        raise SearchException(NOT_FOUND_BY_ID.format(entity_type, entity_id))
    entity_teacher_id = (
        entity.curator_id if entity_type == GROUP else entity.teacher_id
    )
    if entity_teacher_id != teacher.id:
        raise PermissionError(
            PERMISSION_DENIED.format(str(teacher.id))
        )  # message should be changed
    return entity


def check_accessibility_for_name_and_year(
    subject, subject_json, model, checked_entity
):
    year = subject_json.get("year", None)
    name = subject_json.get("name", None)
    if year or name:
        year, name = year or subject.year, name or subject.name
        if isinstance(year, int):
            searched_obj = model.get_by_name_and_year(name, year)
            if searched_obj:
                raise SearchException(
                    ALREADY_EXISTS_WITH_YEAR.format(
                        checked_entity,
                        searched_obj.name,
                        searched_obj.year,
                        400,
                    )
                )
        else:
            raise ValidationError({"year": "Not a valid integer"})
