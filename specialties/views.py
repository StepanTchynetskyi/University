from flask import request

from specialties.schemas import SpecialtySchema
from specialties.models import SpecialtyModel
from users.models import TeacherModel
from utils.constants import (
    CREATED_SUCCESSFULLY,
    SPECIALTY,
    TEACHER,
    NOT_FOUND_BY_ID,
    UPDATED_SUCCESSFULLY,
    SUCCESSFULLY_DELETED,
    EntityInfo,
)
from utils.custom_decorators import (
    create_obj_with_name_and_year,
)
from utils.utils import (
    is_active_user,
    update_obj_with_name_and_year,
)


specialty_schema = SpecialtySchema()


@create_obj_with_name_and_year(
    SpecialtyModel, SPECIALTY, specialty_schema, request
)
def create_specialty(specialty, specialty_json):
    is_active_user(specialty_json, TeacherModel, TEACHER)
    specialty.save_to_db()
    specialty_json = specialty_schema.dump(specialty)
    return {
        "message": CREATED_SUCCESSFULLY.format(SPECIALTY, specialty.id),
        "data": specialty_json,
    }, 201


def get_specialties():
    specialties = [
        specialty_schema.dump(specialty)
        for specialty in SpecialtyModel.get_all_records()
    ]
    return {"data": specialties}, 200


def get_specialty(specialty_id):
    specialty = SpecialtyModel.get_by_id(specialty_id)
    if not specialty:
        return {
            "message": NOT_FOUND_BY_ID.format(SPECIALTY, specialty_id)
        }, 400
    return {"data": specialty_schema.dump(specialty)}, 200


def update_specialty(specialty_id):
    specialty_info = EntityInfo(
        specialty_id, SpecialtyModel, specialty_schema, SPECIALTY
    )
    specialty_json = update_obj_with_name_and_year(
        specialty_info, request, user_model=TeacherModel, user_type=TEACHER
    )
    return {
        "message": UPDATED_SUCCESSFULLY.format(SPECIALTY, specialty_id),
        "data": specialty_json,
    }, 200


def delete_specialty(specialty_id):
    specialty = SpecialtyModel.get_by_id(specialty_id)
    if not specialty:
        return {
            "message": NOT_FOUND_BY_ID.format(SPECIALTY, specialty_id)
        }, 400
    specialty.remove_from_db()
    return {
        "message": SUCCESSFULLY_DELETED.format(SPECIALTY, specialty_id)
    }, 200
