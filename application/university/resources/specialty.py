from flask import jsonify, Blueprint, request

from application.university.schemas.specialty import SpecialtySchema
from application.university.models.specialty import SpecialtyModel
from application.university.models.user import TeacherModel
from application.university.utils.constants import (
    CREATED_SUCCESSFULLY,
    DOES_NOT_EXIST,
    NOT_ACTIVE_USER,
    SPECIALTY,
    TEACHER,
    NOT_FOUND_BY_ID,
    SOMETHING_WENT_WRONG,
    UPDATED_SUCCESSFULLY,
    SUCCESSFULLY_DELETED,
    ALREADY_EXISTS_WITH_YEAR,
)
from application.university.utils.custom_exceptions import SearchException
from application.university.utils.process_dates import check_year

specialty_blprnt = Blueprint("specialty", __name__, url_prefix="/specialties")

specialty_schema = SpecialtySchema()


def process_specialty_json(specialty_json):
    teacher_id = specialty_json.get("teacher_id", None)
    if teacher_id:
        teacher = TeacherModel.get_by_id(teacher_id)
        if not teacher:
            raise SearchException(
                DOES_NOT_EXIST.format(TEACHER, teacher_id), 400
            )
        if not teacher.is_active:
            raise SearchException(NOT_ACTIVE_USER.format(TEACHER, teacher_id))
    return specialty_json


@specialty_blprnt.route("/specialty/create", methods=["POST"])
def create_specialty():
    specialty_json = request.get_json()
    specialty = specialty_schema.load(specialty_json)
    specialty_obj = SpecialtyModel.get_by_name_and_year(
        str(specialty_json["name"]), int(specialty_json["year"])
    )
    if specialty_obj:
        return {
            "message": ALREADY_EXISTS_WITH_YEAR.format(
                SPECIALTY, specialty_obj.name, specialty_obj.year
            )
        }, 400
    try:
        process_specialty_json(specialty_json)
    except SearchException as err:
        return {"message: ": str(err)}, err.status_code
    error = specialty.save_to_db()
    if error:
        return {"message": SOMETHING_WENT_WRONG.format(error)}, 400
    return {
        "message": CREATED_SUCCESSFULLY.format(SPECIALTY, specialty.id)
    }, 201


@specialty_blprnt.route("/", methods=["GET"])
def get_specialties():
    specialties = [
        specialty_schema.dump(specialty)
        for specialty in SpecialtyModel.get_all_records()
    ]
    print(SpecialtyModel.get_all_records())
    return jsonify(specialties), 200


@specialty_blprnt.route("/specialty/<uuid:specialty_id>", methods=["GET"])
def get_specialty(specialty_id):
    specialty = SpecialtyModel.get_by_id(specialty_id)
    if not specialty:
        return {
            "message": NOT_FOUND_BY_ID.format(SPECIALTY, specialty_id)
        }, 400
    return specialty_schema.dump(specialty), 200


@specialty_blprnt.route("/specialty/<uuid:specialty_id>", methods=["PUT"])
def update_specialty(specialty_id):
    specialty = SpecialtyModel.get_by_id(specialty_id)
    if not specialty:
        return {
            "message": NOT_FOUND_BY_ID.format(SPECIALTY, specialty_id)
        }, 400
    specialty_json = request.get_json()
    try:
        process_specialty_json(specialty_json)
    except SearchException as err:
        return {"message: ": str(err)}, err.status_code
    year = specialty_json.get("year", None)
    if year:
        try:
            check_year(SpecialtyModel, year, specialty.name, SPECIALTY)
        except SearchException as err:
            return {"message: ": str(err)}, err.status_code
    specialty = specialty_schema.load(
        specialty_json, instance=specialty, partial=True
    )
    error = specialty.save_to_db()
    if error:
        return {"message": SOMETHING_WENT_WRONG.format(error)}, 400
    return {
        "message": UPDATED_SUCCESSFULLY.format(SPECIALTY, specialty_id)
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
