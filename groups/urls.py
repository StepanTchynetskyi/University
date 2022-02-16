from flask import Blueprint
from groups import views

mod = Blueprint("group", __name__, url_prefix="/groups")

mod.add_url_rule(
    "/group/create", view_func=views.create_group, methods=["POST"]
)
mod.add_url_rule("/", view_func=views.get_groups, methods=["GET"])
mod.add_url_rule(
    "/group/<uuid:group_id>", view_func=views.get_group, methods=["GET"]
)
mod.add_url_rule(
    "/group/<uuid:group_id>", view_func=views.update_group, methods=["PUT"]
)
mod.add_url_rule(
    "/group/<uuid:group_id>",
    view_func=views.delete_position,
    methods=["DELETE"],
)
