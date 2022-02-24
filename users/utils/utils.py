from typing import Union, List, Dict, Type
from uuid import UUID
from flask.wrappers import Request

from subjects import models as subject_models
from users import models as user_models
from users import schemas as user_schemas
from utils.constants import (
    NOT_FOUND_BY_ID,
    ITEM_NOT_PROVIDED,
    STUDENT,
    SUBJECT,
    ITEM_NOT_FOUND_IN_ARRAY,
)
from utils.custom_exceptions import SearchException, NotProvided


def update_specific_user(
    specific_user: Union[user_models.StudentModel, user_models.TeacherModel],
    specific_schema: Union[
        user_schemas.StudentSchema, user_schemas.TeacherSchema
    ],
    request: Request,
) -> Dict:
    """Updates specific user(Student or Teacher)

    :param specific_user: a specific user(Student or Teacher), that should be updated
    :type specific_user: Union[StudentModel, TeacherModel]
    :param specific_schema: specific user schema(StudentSchema or TeacherSchema)
    :type specific_schema: Union[StudentModel, TeacherModel]
    :param request: request from Flask
    :type request: Request
    :return:
    """
    specific_user_json = request.get_json()
    specific_user = specific_schema.load(
        specific_user_json, instance=specific_user, partial=True
    )
    specific_user.save_to_db()
    return specific_schema.dump(specific_user)


def get_items(
    item_type: Union[STUDENT, SUBJECT],
    item_ids: List[UUID],
    item_model: Union[
        Type[user_models.StudentModel], Type[subject_models.SubjectModel]
    ],
) -> List[Union[user_models.StudentModel, subject_models.SubjectModel]]:
    items = item_model.get_by_ids(item_ids)
    if not items:
        raise SearchException(NOT_FOUND_BY_ID.format(item_type, item_ids))
    not_found_ids = [item.id for item in items if item.id not in item_ids]
    if not_found_ids:
        raise SearchException(NOT_FOUND_BY_ID.format(item_type, not_found_ids))
    return items


def remove_items_from_entity(
    entity_items, entity_type, entity_id, items, item_type
):
    for item in items:
        if item in entity_items:
            entity_items.remove(item)
        else:
            raise SearchException(
                ITEM_NOT_FOUND_IN_ARRAY.format(
                    item_type, item.id, entity_type, entity_id
                )
            )
