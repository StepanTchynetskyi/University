from flask import Blueprint

from positions import views
from users import urls as user_urls

mod = Blueprint("position", __name__, url_prefix="/positions")
mod_with_uuid = Blueprint(
    "position_with_uuid", __name__, url_prefix="/<uuid:position_id>"
)
mod.register_blueprint(mod_with_uuid)

user_urls.teacher_mod_with_uuid.register_blueprint(mod)
#  /users/teachers/positions/create
mod.add_url_rule("/create", view_func=views.create_position, methods=["POST"])

#  /users/teachers/positions/
mod.add_url_rule("/", view_func=views.get_positions, methods=["GET"])

#  /users/teachers/positions/<position_id>/
mod_with_uuid.add_url_rule("/", view_func=views.get_position, methods=["GET"])
mod_with_uuid.add_url_rule(
    "/", view_func=views.update_position, methods=["PUT"]
)
mod_with_uuid.add_url_rule(
    "/", view_func=views.delete_position, methods=["DELETE"]
)
