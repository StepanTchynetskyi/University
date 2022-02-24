from flask import Blueprint
from groups import views

mod = Blueprint("group", __name__, url_prefix="/groups")
mod_with_uuid = Blueprint("group", __name__, url_prefix="/<uuid:group_id>")
mod.register_blueprint(mod_with_uuid)
mod.add_url_rule("/create", view_func=views.create_group, methods=["POST"])
mod.add_url_rule("/", view_func=views.get_groups, methods=["GET"])
mod_with_uuid.add_url_rule("/", view_func=views.get_group, methods=["GET"])
mod_with_uuid.add_url_rule("/", view_func=views.update_group, methods=["PUT"])
mod_with_uuid.add_url_rule(
    "/",
    view_func=views.delete_position,
    methods=["DELETE"],
)
