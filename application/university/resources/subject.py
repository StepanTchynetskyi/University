from flask import jsonify, Blueprint, request

from application.university.schemas.subject import SubjectSchema
from application.university.models.subject import SubjectModel
from application.university.utils.constants import (
    SOMETHING_WENT_WRONG,
    CREATED_SUCCESSFULLY,
    SUBJECT,
    NOT_FOUND_BY_ID,
    UPDATED_SUCCESSFULLY,
    SUCCESSFULLY_DELETED,
    ALREADY_EXISTS_WITH_YEAR,
)
from application.university.utils.custom_exceptions import SearchException
from application.university.utils.process_dates import check_year

subject_blprnt = Blueprint("subject", __name__, url_prefix="/subjects")

subject_schema = SubjectSchema()


@subject_blprnt.route("/subject/create", methods=["POST"])
def create_subject():
    subject_json = request.get_json()
    subject = subject_schema.load(subject_json)
    subject_obj = SubjectModel.get_by_name_and_year(
        subject_json["name"], subject_json["year"]
    )
    if subject_obj:
        return {
            "message": ALREADY_EXISTS_WITH_YEAR.format(
                SUBJECT, subject_obj.name, subject_obj.year
            )
        }, 400
    error = subject.save_to_db()
    if error:
        return {"message": SOMETHING_WENT_WRONG.format(error)}, 400
    return {"message": CREATED_SUCCESSFULLY.format(SUBJECT, subject.id)}, 201


@subject_blprnt.route("/", methods=["GET"])
def get_subjects():
    subjects = [
        subject_schema.dump(subject)
        for subject in SubjectModel.get_all_records()
    ]
    return jsonify(subjects), 200


@subject_blprnt.route("/subject/<uuid:subject_id>", methods=["GET"])
def get_subject(subject_id):
    subject = SubjectModel.get_by_id(subject_id)
    if not subject:
        return {"message": NOT_FOUND_BY_ID.format(SUBJECT, subject_id)}, 400
    return subject_schema.dump(subject), 200


@subject_blprnt.route("/subject/<uuid:subject_id>", methods=["PUT"])
def update_subject(subject_id):
    subject = SubjectModel.get_by_id(subject_id)
    if not subject:
        return {"message": NOT_FOUND_BY_ID.format(SUBJECT, subject_id)}, 400
    subject_json = request.get_json()
    year = subject_json.get("year", None)
    if year:
        try:
            check_year(SubjectModel, year, subject.name, SUBJECT)
        except SearchException as err:
            return {"message: ": str(err)}, err.status_code
    subject = subject_schema.load(subject_json, instance=subject, partial=True)
    error = subject.save_to_db()
    if error:
        return {"message": SOMETHING_WENT_WRONG.format(error)}, 400
    return {"message": UPDATED_SUCCESSFULLY.format(SUBJECT, subject_id)}, 200


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
