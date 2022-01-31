from flask import jsonify, Blueprint, request

from application.university.schemas.group import GroupSchema
from application.university.models.group import GroupModel
from application.university.models.user import TeacherModel
from application.university.utils.custom_exceptions import SearchException
from application.university.utils.process_dates import check_year
from application.university.utils.constants import (
    GROUP,
    ALREADY_EXISTS_WITH_YEAR,
    SOMETHING_WENT_WRONG,
    CREATED_SUCCESSFULLY,
    NOT_FOUND_BY_ID,
    UPDATED_SUCCESSFULLY,
    CURATOR,
    SUCCESSFULLY_DELETED,
)

group_blprnt = Blueprint("group", __name__, url_prefix="/groups")

group_schema = GroupSchema()


@group_blprnt.route("/group/create", methods=["POST"])
def create_group():
    group_json = request.get_json()
    group = group_schema.load(group_json)
    group_obj = GroupModel.get_by_name_and_year(
        str(group_json["name"]), int(group_json["year"])
    )
    if group_obj:
        return {
            "message": ALREADY_EXISTS_WITH_YEAR.format(
                GROUP, group_obj.name, group_obj.year
            )
        }, 400
    curator_id = group_json.get("curator_id", None)
    if curator_id:
        curator = TeacherModel.get_by_id(curator_id)
        if not curator:
            return {
                "message": NOT_FOUND_BY_ID.format(CURATOR, curator_id)
            }, 400
    error = group.save_to_db()
    if error:
        return {"message": SOMETHING_WENT_WRONG.format(error)}, 400
    return {"message": CREATED_SUCCESSFULLY.format(GROUP, group.id)}, 201


@group_blprnt.route("/", methods=["GET"])
def get_groups():
    groups = [
        group_schema.dump(group) for group in GroupModel.get_all_records()
    ]
    return jsonify(groups), 200


@group_blprnt.route("/group/<uuid:group_id>", methods=["GET"])
def get_group(group_id):
    group = GroupModel.get_by_id(group_id)
    if not group:
        return {"message": NOT_FOUND_BY_ID.format(GROUP, group_id)}, 400
    return group_schema.dump(group), 200


@group_blprnt.route("/group/<uuid:group_id>", methods=["PUT"])
def update_group(group_id):
    group = GroupModel.get_by_id(group_id)
    if not group:
        return {"message": NOT_FOUND_BY_ID.format(GROUP, group_id)}, 400
    group_json = request.get_json()
    curator_id = group_json.get("curator_id", None)
    if curator_id:
        curator = TeacherModel.get_by_id(curator_id)
        if not curator:
            return {
                "message: ": NOT_FOUND_BY_ID.format(CURATOR, curator_id)
            }, 400
    year = group_json.get("year", None)
    if year:
        try:
            check_year(GroupModel, year, group.name, GROUP)
        except SearchException as err:
            return {"message: ": str(err)}, err.status_code
    group = group_schema.load(group_json, instance=group, partial=True)
    error = group.save_to_db()
    if error:
        return {"message": SOMETHING_WENT_WRONG.format(error)}, 400
    return {"message": UPDATED_SUCCESSFULLY.format(GROUP, group_id)}, 200


@group_blprnt.route("/group/<uuid:group_id>", methods=["DELETE"])
def delete_position(group_id):
    group = GroupModel.get_by_id(group_id)
    if not group:
        return {"message": NOT_FOUND_BY_ID.format(GROUP, group_id)}, 400
    group.remove_from_db()
    return {"message": SUCCESSFULLY_DELETED.format(GROUP, group_id)}, 200


@group_blprnt.route(
    "/group/<uuid:group_id>/appoint-students/appoint-student/<uuid:student_id>",
    methods=["POST"],
)
def appoint_student_to_group(group_id, student_id):
    return {"message: ": "TODO"}, 200


@group_blprnt.route(
    "/group/<uuid:group_id>/appoint-students", methods=["POST"]
)
def appoint_students_to_group(group_id):
    # TODO: add students from group, and students from list of UUIDs
    return {"message: ": "TODO"}, 200


@group_blprnt.route(
    "/group/<uuid:group_id>/appoint-subjects/appoint-subject/<uuid:subject_id>",
    methods=["POST"],
)
def appoint_subject_to_group(group_id, subject_id):
    return {"message: ": "TODO"}, 200


@group_blprnt.route(
    "/group/<uuid:group_id>/appoint-subjects", methods=["POST"]
)
def appoint_subjects_to_groups(group_id):
    return {"message: ": "TODO"}, 200
