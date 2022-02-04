from flask import jsonify, Blueprint, request

from application.university.schemas.subject import SubjectSchema
from application.university.models.subject import SubjectModel
from application.university.utils.constants import (
    CREATED_SUCCESSFULLY,
    SUBJECT,
    NOT_FOUND_BY_ID,
    UPDATED_SUCCESSFULLY,
    SUCCESSFULLY_DELETED,
    EntityInfo,
)
from application.university.utils.custom_decorators import (
    create_obj_with_name_and_year,
)
from application.university.utils.utils import update_obj_with_name_and_year

subject_blprnt = Blueprint("subject", __name__, url_prefix="/subjects")

subject_schema = SubjectSchema()


@subject_blprnt.route("/subject/create", methods=["POST"])
@create_obj_with_name_and_year(SubjectModel, SUBJECT, subject_schema, request)
def create_subject(subject, subject_json):
    subject.save_to_db()
    return {
        "message": CREATED_SUCCESSFULLY.format(SUBJECT, subject.id),
        "data": subject_json,
    }, 201


@subject_blprnt.route("/", methods=["GET"])
def get_subjects():
    subjects = [
        subject_schema.dump(subject)
        for subject in SubjectModel.get_all_records()
    ]
    return {"data": subjects}, 200


@subject_blprnt.route("/subject/<uuid:subject_id>", methods=["GET"])
def get_subject(subject_id):
    subject = SubjectModel.get_by_id(subject_id)
    if not subject:
        return {"message": NOT_FOUND_BY_ID.format(SUBJECT, subject_id)}, 400
    return {"data": subject_schema.dump(subject)}, 200


@subject_blprnt.route("/subject/<uuid:subject_id>", methods=["PUT"])
def update_subject(subject_id):
    subject_info = EntityInfo(
        subject_id, SubjectModel, subject_schema, SUBJECT
    )
    subject_json = update_obj_with_name_and_year(subject_info, request)
    return {
        "message": UPDATED_SUCCESSFULLY.format(SUBJECT, subject_id),
        "data": subject_json,
    }, 200


# TODO: check if many-to-many relation disappear
@subject_blprnt.route("/subject/<uuid:subject_id>", methods=["DELETE"])
def delete_subject(subject_id):
    subject = SubjectModel.get_by_id(subject_id)
    if not subject:
        return {"message": NOT_FOUND_BY_ID.format(SUBJECT, subject_id)}, 400
    subject.remove_from_db()
    return {"message": SUCCESSFULLY_DELETED.format(SUBJECT, subject_id)}, 200


@subject_blprnt.route(
    "/subject/<uuid:subject_id>/appoint-teachers/appoint-teacher/<uuid:teacher_id>",
    methods=["POST"],
)
def appoint_teacher_to_subject(subject_id, teacher_id):
    return {"message: ": "TODO"}, 200


@subject_blprnt.route(
    "/subject/<uuid:subject_id>/appoint-teachers", methods=["POST"]
)
def appoint_teachers_to_subject(subject_id):
    # TODO: appoint teachers to subjects from array of UUIDs
    return {"message: ": "TODO"}, 200


@subject_blprnt.route(
    "/subject/<uuid:subject_id>/appoint-groups/appoint-group/<uuid:group_id>",
    methods=["POST"],
)
def appoint_group_to_subject(subject_id, group_id):
    return {"message: ": "TODO"}, 200


@subject_blprnt.route(
    "/subject/<uuid:subject_id>/appoint-groups", methods=["POST"]
)
def appoint_groups_to_subject(subject_id):
    # TODO: appoint groups to subjects from array of UUIDs or as in previous years
    return {"message: ": "TODO"}, 200


@subject_blprnt.route(
    "/subject/<uuid:subject_id>/appoint-specialties/appoint-specialty/<uuid:specialty_id>",
    methods=["POST"],
)
def appoint_specialty_to_subject(subject_id, specialty_id):
    return {"message: ": "TODO"}, 200


@subject_blprnt.route(
    "/subject/<uuid:subject_id>/appoint-specialties", methods=["POST"]
)
def appoint_specialties_to_subject(subject_id):
    # TODO: appoint specialties to subject from array of UUIDs
    return {"message: ": "TODO"}, 200