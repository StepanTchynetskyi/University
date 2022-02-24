from flask import request

from groups import schemas as group_schemas
from groups import models as group_models
from users import models as user_models
from utils.custom_decorators import (
    create_obj_with_name_and_year,
)
from utils.constants import (
    GROUP,
    CREATED_SUCCESSFULLY,
    NOT_FOUND_BY_ID,
    UPDATED_SUCCESSFULLY,
    CURATOR,
    SUCCESSFULLY_DELETED,
    EntityInfo,
)
from utils.utils import (
    is_active_user,
    update_obj_with_name_and_year,
)


group_schema = group_schemas.GroupSchema()


@create_obj_with_name_and_year(
    group_models.GroupModel, GROUP, group_schema, request
)
def create_group(group, group_json):
    is_active_user(group_json, CURATOR)
    group.save_to_db()
    group_json = group_schema.dump(group)
    return {
        "message": CREATED_SUCCESSFULLY.format(GROUP, group.id),
        "data": group_json,
    }, 201


def get_groups():
    groups = [
        group_schema.dump(group)
        for group in group_models.GroupModel.get_all_records()
    ]
    return {"data": {"groups": groups}}, 200


def get_group(group_id):
    group = group_models.GroupModel.get_by_id(group_id)
    if not group:
        return {"message": NOT_FOUND_BY_ID.format(GROUP, group_id)}, 400
    return {"data": group_schema.dump(group)}, 200


def update_group(group_id):
    group_info = EntityInfo(
        group_id, group_models.GroupModel, group_schema, GROUP
    )
    group_json = update_obj_with_name_and_year(
        group_info,
        request,
        user_model=user_models.TeacherModel,
        user_type=CURATOR,
    )
    return {
        "message": UPDATED_SUCCESSFULLY.format(GROUP, group_id),
        "data": group_json,
    }, 200


def delete_position(group_id):
    group = group_models.GroupModel.get_by_id(group_id)
    if not group:
        return {"message": NOT_FOUND_BY_ID.format(GROUP, group_id)}, 400
    group.remove_from_db()
    return {"message": SUCCESSFULLY_DELETED.format(GROUP, group_id)}, 200
