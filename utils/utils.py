from typing import Dict, Type, Union
import uuid

import bcrypt

from marshmallow import ValidationError
from flask import Request

from groups.models import GroupModel
from specialties.models import SpecialtyModel
from subjects.models import SubjectModel
from users.models import TeacherModel, StudentModel
from utils.constants import (
    DOES_NOT_EXIST,
    NOT_ACTIVE_USER,
    NOT_FOUND_BY_ID,
    PERMISSION_DENIED,
    GROUP,
    ALREADY_EXISTS_WITH_YEAR,
    EntityInfo,
)
from utils.custom_exceptions import (
    SearchException,
)


def is_active_user(
    json_: Dict, user_model: Type[TeacherModel], user_type: str
) -> None:
    """Checks for an active user

    :param json_: user_json
    :param user_model: a specific user model
    :type user_model: TeacherModel
    :param user_type: a specific user type('Teacher')
    :type user_type: str
    :return: None
    :raises:
        SearchException: if teacher not found or teacher is not active
    """
    user_id = json_.get("teacher_id", None)
    if user_id:
        teacher = user_model.get_by_id(user_id)
        if not teacher:
            raise SearchException(
                DOES_NOT_EXIST.format(user_type, user_id), 404
            )
        if not teacher.is_active:
            raise SearchException(NOT_ACTIVE_USER.format(user_type, user_id))


def get_hashed_password(plain_text_password: bytes) -> bytes:
    """Converts bytes to hash

    :param plain_text_password: encoded (utf-8) string password
    :type plain_text_password: bytes
    :return: hashed password
    """
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())


def check_password(plain_text_password: str, hashed_password: str) -> bool:
    """Checks if the password matches

    :param plain_text_password: text password
    :param hashed_password: hashed password
    :return: True if the password matches, otherwise False
    """
    return bcrypt.checkpw(
        plain_text_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def update_obj_with_name_and_year(
    entity_info: EntityInfo,
    request: Request,
    *,
    user_model: Union[Type[StudentModel], Type[TeacherModel]] = None,
    user_type: str = None
) -> Dict:
    """Updates

    :param entity_info: named tuple that contains: id, model, schema, type.
    Entities: Subject, Specialty or Group
    :type entity_info: EntityInfo
    :param request: a Flask request
    :type request: Request
    :param user_model: a specific user model
    :type user_model: Union[Type[StudentModel], Type[TeacherModel]]
    :param user_type: a specific user type('Teacher', 'Student')
    :type user_type: str
    :return: a user json
    :raises:
        SearchException: if entity object is not found
    """
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


def get_entity_with_teacher(
    teacher: TeacherModel,
    entity_id: uuid.UUID,
    entity_model: Type[GROUP],
    entity_type: str,
) -> GROUP:
    """Gets entity that has a teacher foreign key

    :param teacher: teacher user
    :type teacher: TeacherModel
    :param entity_id: unique entity id.
    Entities: Group
    :param entity_model: a specific model
    :type entity_model: Type[Group]
    :param entity_type: a specific entity type
    :type entity_type: str
    :return: specific entity object
    """
    entity = entity_model.get_by_id(entity_id)
    if not entity:
        raise SearchException(NOT_FOUND_BY_ID.format(entity_type, entity_id))
    entity_teacher_id = (
        entity.curator_id if entity_type == GROUP else entity.teacher_id
    )
    if entity_teacher_id != teacher.id:
        raise PermissionError(PERMISSION_DENIED.format(str(teacher.id)))
    return entity


def check_accessibility_for_name_and_year(
    entity_obj: Union[SubjectModel, GroupModel, SpecialtyModel],
    entity_json: Dict,
    model: Union[Type[SubjectModel], Type[GroupModel], Type[SpecialtyModel]],
    entity_type: str,
) -> None:
    """Checks accessibility for objects with name and year

    :param entity_obj: specific entity
    Entities: SubjectModel, GroupModel, SpecialtyModel
    :type entity_obj: Union[SubjectModel, GroupModel, SpecialtyModel],
    :param entity_json: json with an entity data
    :type entity_json: Dict
    :param model: a specific entity model
    :type model: Union[Type[SubjectModel], Type[GroupModel], Type[SpecialtyModel]]
    :param entity_type: a specific entity type
    :type entity_type: str
    :return: None
    :raises:
        SearchException: if entity object with name and year already exists
    """
    year = entity_json.get("year", None)
    name = entity_json.get("name", None)
    if year or name:
        year, name = year or entity_obj.year, name or entity_obj.name
        if isinstance(year, int):
            searched_obj = model.get_by_name_and_year(name, year)
            if searched_obj:
                raise SearchException(
                    ALREADY_EXISTS_WITH_YEAR.format(
                        entity_type,
                        searched_obj.name,
                        searched_obj.year,
                        400,
                    )
                )
        else:
            raise ValidationError({"year": "Not a valid integer"})


def validate_uuid(uuid_: str) -> None:
    """Validates string like UUID

    :param uuid_: uuid that should be checked
    :type uuid_: str
    :return: None
    :raises:
        ValueError: if uuid is not valid
    """
    try:
        uuid.UUID(uuid_, version=4)
    except ValueError:
        raise ValueError("Invalid uuid <uuid={}>".format(uuid_))
