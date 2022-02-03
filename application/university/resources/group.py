from flask import jsonify, Blueprint, request

from application.university.schemas.group import GroupSchema
from application.university.models.group import GroupModel
from application.university.models.user import TeacherModel
from application.university.utils.custom_decorators import (
    create_obj_with_name_and_year,
)
from application.university.utils.constants import (
    GROUP,
    CREATED_SUCCESSFULLY,
    NOT_FOUND_BY_ID,
    UPDATED_SUCCESSFULLY,
    CURATOR,
    SUCCESSFULLY_DELETED,
    EntityInfo,
)
from application.university.utils.utils import (
    is_active_user,
    update_obj_with_name_and_year,
)

group_blprnt = Blueprint("group", __name__, url_prefix="/groups")

group_schema = GroupSchema()


@group_blprnt.route("/group/create", methods=["POST"])
@create_obj_with_name_and_year(GroupModel, GROUP, group_schema, request)
def create_group(group, group_json):
    is_active_user(group_json, TeacherModel, CURATOR)
    group.save_to_db()
    group_json = group_schema.dump(group)
    return {
        "message": CREATED_SUCCESSFULLY.format(GROUP, group.id),
        "data": group_json,
    }, 201


@group_blprnt.route("/", methods=["GET"])
def get_groups():
    groups = [
        group_schema.dump(group) for group in GroupModel.get_all_records()
    ]
    return {"data": groups}, 200


@group_blprnt.route("/group/<uuid:group_id>", methods=["GET"])
def get_group(group_id):
    group = GroupModel.get_by_id(group_id)
    if not group:
        return {"message": NOT_FOUND_BY_ID.format(GROUP, group_id)}, 400
    return {"data": group_schema.dump(group)}, 200


@group_blprnt.route("/group/<uuid:group_id>", methods=["PUT"])
def update_group(group_id):
    group_info = EntityInfo(group_id, GroupModel, group_schema, GROUP)
    group_json = update_obj_with_name_and_year(
        group_info, request, user_model=TeacherModel, user_type=CURATOR
    )
    return {
        "message": UPDATED_SUCCESSFULLY.format(GROUP, group_id),
        "data": group_json,
    }, 200


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
