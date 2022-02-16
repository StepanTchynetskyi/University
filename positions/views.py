from flask import request

from positions.models import PositionModel
from positions.schemas import PositionSchema
from utils.constants import (
    CREATED_SUCCESSFULLY,
    NOT_FOUND_BY_ID,
    POSITION,
    UPDATED_SUCCESSFULLY,
    SUCCESSFULLY_DELETED,
    ALREADY_EXISTS,
)

position_schema = PositionSchema()


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


def get_positions():
    positions = [
        position_schema.dump(position)
        for position in PositionModel.get_all_records()
    ]
    return {"data": positions}, 200


def get_position(position_id):
    position = PositionModel.get_by_id(position_id)
    if not position:
        return {"message": NOT_FOUND_BY_ID.format(POSITION, position_id)}, 400
    return {"data": position_schema.dump(position)}, 200


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


def delete_position(position_id):
    position = PositionModel.get_by_id(position_id)
    if not position:
        return {"message": NOT_FOUND_BY_ID.format(POSITION, position_id)}, 400
    position.remove_from_db()
    return {"message": SUCCESSFULLY_DELETED.format(POSITION, position_id)}, 200
