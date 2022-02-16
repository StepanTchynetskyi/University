from flask import Blueprint

from specialties import views

mod = Blueprint("specialty", __name__, url_prefix="/specialties")

mod.add_url_rule(
    "/specialty/create", view_func=views.create_specialty, methods=["POST"]
)
mod.add_url_rule("/", view_func=views.get_specialties, methods=["GET"])
mod.add_url_rule(
    "/specialty/<uuid:specialty_id>",
    view_func=views.get_specialty,
    methods=["GET"],
)
mod.add_url_rule(
    "/specialty/<uuid:specialty_id>",
    view_func=views.update_specialty,
    methods=["PUT"],
)
mod.add_url_rule(
    "/specialty/<uuid:specialty_id>",
    view_func=views.delete_specialty,
    methods=["DELETE"],
)
