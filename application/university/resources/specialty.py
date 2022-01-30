from dateutil import parser

from flask import jsonify, Blueprint, request

from application.university.schemas.specialty import SpecialtySchema
from application.university.models.specialty import SpecialtyModel
from application.university.models.user import TeacherModel
from application.university.utils.constants import (
    CREATED_SUCCESSFULLY,
    DOES_NOT_EXIST,
    DATE_NOT_PROVIDED,
    NOT_ACTIVE_USER,
    SPECIALTY,
    TEACHER,
    NOT_FOUND_BY_ID,
    SOMETHING_WENT_WRONG,
    UPDATED_SUCCESSFULLY,
    SUCCESSFULLY_DELETED,
)
from application.university.utils.custom_exceptions import UserSearchException

specialty_blprnt = Blueprint("specialty", __name__, url_prefix="/specialties")

specialty_schema = SpecialtySchema()


def process_specialty_json(specialty_json):
    specialty_date = specialty_json.get("specialty_date", None)
    if specialty_date:
        specialty_date = parser.parse(specialty_date).date()
        specialty_json["specialty_date"] = str(specialty_date)
    teacher_id = specialty_json.get("teacher_id", None)
    if teacher_id:
        teacher = TeacherModel.get_by_id(teacher_id)
        if not teacher:
            raise UserSearchException(
                DOES_NOT_EXIST.format(TEACHER, teacher_id), 400
            )
        if not teacher.is_active:
            raise UserSearchException(
                NOT_ACTIVE_USER.format(TEACHER, teacher_id)
            )
    return specialty_json


@specialty_blprnt.route("/specialty/create", methods=["POST"])
def create_specialty():
    specialty_json = request.get_json()
    specialty_date = specialty_json.get("specialty_date", None)
    if not specialty_date:
        return {"message: ": DATE_NOT_PROVIDED}, 400
    try:
        specialty_json = process_specialty_json(specialty_json)
    except parser.ParserError as err:
        return {"message: ": str(err)}, 400
    except UserSearchException as err:
        return {"message: ": str(err)}, err.status_code

    specialty = specialty_schema.load(specialty_json)
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
    return jsonify(specialties), 200


@specialty_blprnt.route("/specialty/<uuid:specialty_id>", methods=["GET"])
def get_specialty(specialty_id):
    specialty = SpecialtyModel.get_by_id(specialty_id)
    if not specialty:
        return {
            "message": NOT_FOUND_BY_ID.format(SPECIALTY, specialty_id)
        }, 400
    return {"message": specialty_schema.dump(specialty)}, 200


@specialty_blprnt.route("/specialty/<uuid:specialty_id>", methods=["PUT"])
def update_specialty(specialty_id):
    specialty = SpecialtyModel.get_by_id(specialty_id)
    if not specialty:
        return {
            "message": NOT_FOUND_BY_ID.format(SPECIALTY, specialty_id)
        }, 400
    specialty_json = request.get_json()
    try:
        specialty_json = process_specialty_json(specialty_json)
    except parser.ParserError as err:
        return {"message: ": str(err)}, 400
    except UserSearchException as err:
        return {"message: ": str(err)}, err.status_code
    specialty = specialty_schema.load(specialty_json)
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
    return {"message": SUCCESSFULLY_DELETED.format(SPECIALTY, specialty_id)}
