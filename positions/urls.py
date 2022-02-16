from flask import Blueprint

from positions import views

mod = Blueprint("position", __name__, url_prefix="/users/teachers/positions")

mod.add_url_rule(
    "/position/create", view_func=views.create_position, methods=["POST"]
)
mod.add_url_rule("/", view_func=views.get_positions, methods=["GET"])
mod.add_url_rule(
    "/position/<uuid:position_id>",
    view_func=views.get_position,
    methods=["GET"],
)
mod.add_url_rule(
    "/position/<uuid:position_id>",
    view_func=views.update_position,
    methods=["PUT"],
)
mod.add_url_rule(
    "/position/<uuid:position_id>",
    view_func=views.delete_position,
    methods=["DELETE"],
)
