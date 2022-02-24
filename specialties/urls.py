from flask import Blueprint

from specialties import views

mod = Blueprint("specialty", __name__, url_prefix="/specialties")
mod_with_uuid = Blueprint(
    "specialty_with_uuid", __name__, url_prefix="/<uuid:specialty_id>"
)
mod.register_blueprint(mod_with_uuid)

# /specialties/create
mod.add_url_rule("/create", view_func=views.create_specialty, methods=["POST"])

# /specialties/
mod.add_url_rule("", view_func=views.get_specialties, methods=["GET"])

# /specialties/<specialty_id>/
mod_with_uuid.add_url_rule("", view_func=views.get_specialty, methods=["GET"])
mod_with_uuid.add_url_rule(
    "", view_func=views.update_specialty, methods=["PUT"]
)
mod_with_uuid.add_url_rule(
    "", view_func=views.delete_specialty, methods=["DELETE"]
)
