from flask import Blueprint, request

from application.university.models.position import PositionModel
from application.university.schemas.position import PositionSchema
from application.university.utils.constants import (
    CREATED_SUCCESSFULLY,
    NOT_FOUND_BY_ID,
    POSITION,
    UPDATED_SUCCESSFULLY,
    SUCCESSFULLY_DELETED,
    ALREADY_EXISTS,
)

# TODO: should be just for admin
position_blprnt = Blueprint(
    "position", __name__, url_prefix="/users/teachers/positions"
)

position_schema = PositionSchema()


@position_blprnt.route("/position/create", methods=["POST"])
def create_position():
    position_json = request.get_json()
    position = PositionModel.get_by_position_name(
        str(position_json.get("position_name", None))
    )
    if position:
        return {
            "message": ALREADY_EXISTS.format(POSITION, position.position_name)
        }, 400
    position = position_schema.load(position_json)
    position.save_to_db()
    position_json = position_schema.dump(position)
    return {
        "message": CREATED_SUCCESSFULLY.format(POSITION, position.id),
        "data": position_json,
    }, 201


@position_blprnt.route("/", methods=["GET"])
def get_positions():
    positions = [
        position_schema.dump(position)
        for position in PositionModel.get_all_records()
    ]
    return {"data": positions}, 200


@position_blprnt.route("/position/<uuid:position_id>", methods=["GET"])
def get_position(position_id):
    position = PositionModel.get_by_id(position_id)
    if not position:
        return {"message": NOT_FOUND_BY_ID.format(POSITION, position_id)}, 400
    return {"data": position_schema.dump(position)}, 200


@position_blprnt.route("/position/<uuid:position_id>", methods=["PUT"])
def update_position(position_id):
    position = PositionModel.get_by_id(position_id)
    if not position:
        return {"message": NOT_FOUND_BY_ID.format(POSITION, position_id)}, 400
    position_json = request.get_json()
    position_name = position_json.get("position_name", None)
    if position_name:
        position_obj = PositionModel.get_by_position_name(str(position_name))
        if position_obj:
            return {
                "message": ALREADY_EXISTS.format(
                    POSITION, position_obj.position_name
                )
            }, 400
    position = position_schema.load(
        position_json, instance=position, partial=True
    )
    position.save_to_db()
    position_json = position_schema.dump(position)
    return {
        "message": UPDATED_SUCCESSFULLY.format(POSITION, position_id),
        "data": position_json,
    }, 200


@position_blprnt.route("/position/<uuid:position_id>", methods=["DELETE"])
def delete_position(position_id):
    position = PositionModel.get_by_id(position_id)
    if not position:
        return {"message": NOT_FOUND_BY_ID.format(POSITION, position_id)}, 400
    position.remove_from_db()
    return {"message": SUCCESSFULLY_DELETED.format(POSITION, position_id)}, 200
