from typing import Union, List, Dict, Type
from uuid import UUID
from flask.wrappers import Request

from subjects.models import SubjectModel
from users.models import StudentModel, TeacherModel
from users.schemas import StudentSchema, TeacherSchema
from utils.constants import (
    NOT_FOUND_BY_ID,
    ITEM_NOT_PROVIDED,
    STUDENT,
    SUBJECT,
)
from utils.custom_exceptions import SearchException, NotProvided
from utils.utils import validate_uuid


def update_specific_user(
    specific_user: Union[StudentModel, TeacherModel],
    specific_schema: Union[StudentSchema, TeacherSchema],
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
    item_model: Union[Type[StudentModel], Type[SubjectModel]],
) -> List[Union[StudentModel, SubjectModel]]:
    if not item_ids:
        raise NotProvided(ITEM_NOT_PROVIDED.format(item_type))
    for uuid_ in item_ids:
        validate_uuid(uuid_)
    items = item_model.get_by_ids(item_ids)
    if not items:
        raise SearchException(NOT_FOUND_BY_ID.format(item_type, item_ids))
    not_found_ids = [item.id for item in items if str(item.id) not in item_ids]
    if not_found_ids:
        raise SearchException(NOT_FOUND_BY_ID.format(item_type, not_found_ids))
    return items
