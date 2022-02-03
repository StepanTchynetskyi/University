from flask import jsonify, Blueprint, request

from application.university.schemas.specialty import SpecialtySchema
from application.university.models.specialty import SpecialtyModel
from application.university.models.user import TeacherModel
from application.university.utils.constants import (
    CREATED_SUCCESSFULLY,
    SPECIALTY,
    TEACHER,
    NOT_FOUND_BY_ID,
    UPDATED_SUCCESSFULLY,
    SUCCESSFULLY_DELETED,
    EntityInfo,
)
from application.university.utils.custom_decorators import (
    create_obj_with_name_and_year,
)
from application.university.utils.utils import (
    is_active_user,
    update_obj_with_name_and_year,
)

specialty_blprnt = Blueprint("specialty", __name__, url_prefix="/specialties")

specialty_schema = SpecialtySchema()


@specialty_blprnt.route("/specialty/create", methods=["POST"])
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


@specialty_blprnt.route("/", methods=["GET"])
def get_specialties():
    specialties = [
        specialty_schema.dump(specialty)
        for specialty in SpecialtyModel.get_all_records()
    ]
    return {"data": specialties}, 200


@specialty_blprnt.route("/specialty/<uuid:specialty_id>", methods=["GET"])
def get_specialty(specialty_id):
    specialty = SpecialtyModel.get_by_id(specialty_id)
    if not specialty:
        return {
            "message": NOT_FOUND_BY_ID.format(SPECIALTY, specialty_id)
        }, 400
    return {"data": specialty_schema.dump(specialty)}, 200


@specialty_blprnt.route("/specialty/<uuid:specialty_id>", methods=["PUT"])
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


@specialty_blprnt.route("/specialty/<uuid:specialty_id>", methods=["DELETE"])
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


@specialty_blprnt.route(
    "/specialty/<uuid:specialty_id>/appoint-subjects/appoint-subject/<uuid:subject_id>",
    methods=["POST"],
)
def appoint_subject_to_specialty(specialty_id, subject_id):
    return {"message: ": "TODO"}, 200


@specialty_blprnt.route(
    "/specialty/<uuid:specialty_id>/appoint-subjects", methods=["POST"]
)
def appoint_subjects_to_specialties(specialty_id):
    return {"message: ": "TODO"}, 200
