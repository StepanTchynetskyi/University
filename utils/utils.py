from typing import Dict, Type, Union, List
import uuid

import bcrypt

from flask import Request

from assignments import models as assignment_models
from groups import models as group_models
from specialties import models as specialty_models
from subjects import models as subject_models
from users import models as user_models
from utils.constants import (
    DOES_NOT_EXIST,
    NOT_ACTIVE_USER,
    NOT_FOUND_BY_ID,
    PERMISSION_DENIED,
    GROUP,
    SUBJECT,
    ALREADY_EXISTS_WITH_YEAR,
    EntityInfo,
    ITEM_NOT_FOUND_IN_ARRAY,
)
from utils.custom_exceptions import (
    SearchException,
)


def is_active_user(json_: Dict, user_type: str) -> None:
    """Checks for an active user

    :param json_: user_json
    :type json_: Dict
    :param user_type: a specific user type('Teacher')
    :type user_type: str
    :return: None
    :raises:
        SearchException: if teacher not found or teacher is not active
    """
    user_id = json_.get("teacher_id", None)
    if user_id:
        teacher = user_models.UserModel.get_by_id(user_id)
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
    user_model: Union[
        Type[user_models.StudentModel], Type[user_models.TeacherModel]
    ] = None,
    user_type: str = None,
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
        is_active_user(entity_json, user_type)

    entity_obj = entity_info.schema.load(
        entity_json, instance=entity_obj, partial=True
    )
    check_accessibility_for_name_and_year(
        entity_obj, entity_json, entity_info.model, entity_info.type
    )

    entity_obj.save_to_db()
    entity_json = entity_info.schema.dump(entity_obj)
    return entity_json


def get_entity_with_teacher(
    teacher: user_models.TeacherModel,
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
    if entity_type == SUBJECT:
        entity_teacher_ids = [teacher.id for teacher in entity.teachers]
    else:
        entity_teacher_ids = (
            entity.curator_id if entity_type == GROUP else entity.teacher_id,
        )
    if teacher.id not in entity_teacher_ids:
        raise PermissionError(PERMISSION_DENIED.format(str(teacher.id)))
    return entity


def check_accessibility_for_name_and_year(
    entity_obj: Union[
        subject_models.SubjectModel,
        group_models.GroupModel,
        specialty_models.SpecialtyModel,
    ],
    entity_json: Dict,
    model: Union[
        Type[subject_models.SubjectModel],
        Type[group_models.GroupModel],
        Type[specialty_models.SpecialtyModel],
    ],
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
    year = entity_json.get("year", None) or entity_obj.year
    name = entity_json.get("name", None) or entity_obj.name
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


def get_entity(
    entity_id: uuid.UUID,
    entity_model: Type[subject_models.SubjectModel],
    entity_type: str,
) -> subject_models.SubjectModel:
    """Gets a specific entity

    :param entity_id: a specific entity id
    :type entity_id: UUID
    :param entity_model: a specific entity model
    :type entity_model: Type[SubjectModel]
    :param entity_type: a specific entity type("SUBJECT")
    :type entity_type: str
    :return: a specific entity object
    :raises:
        SearchException: if entity not found
    """
    entity = entity_model.get_by_id(entity_id)
    if not entity:
        raise SearchException(DOES_NOT_EXIST.format(entity_type, entity_id))
    return entity


def get_item_from_entity(
    entity_id: uuid.UUID,
    entity_items: List[
        Union[subject_models.SubjectModel, assignment_models.AssignmentModel]
    ],
    item_id: uuid.UUID,
    entity_type: str,
    item_type: str,
) -> Union[subject_models.SubjectModel, assignment_models.AssignmentModel]:
    """Gets an item from the entity items list

    :param entity_id: a specific entity uuid
    :type entity_id: UUID
    :param entity_items: list of entity items
    :type entity_items:List[Union[SubjectModel, AssignmentModel]]
    :param item_id: searched item uuid
    :type item_id: UUID
    :param entity_type: entity type (Teacher)
    :type entity_type: str
    :param item_type: searched item type (Subject, Assignment)
    :type item_type: str
    :return: searched item (SubjectModel, AssignmentModel)
    :raises:
        SearchException: if item not found in entity items
    """
    for item in entity_items:
        if str(item.id) == str(item_id):
            return item
    else:
        raise SearchException(
            ITEM_NOT_FOUND_IN_ARRAY.format(
                item_type, item_id, entity_type, entity_id
            )
        )
