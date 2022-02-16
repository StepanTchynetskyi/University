from flask import Blueprint

from subjects import views

mod = Blueprint("subject", __name__, url_prefix="/subjects")

mod.add_url_rule(
    "/subject/create", view_func=views.create_subject, methods=["POST"]
)
mod.add_url_rule("/", view_func=views.get_subjects, methods=["GET"])
mod.add_url_rule(
    "/subject/<uuid:subject_id>", view_func=views.get_subject, methods=["GET"]
)
mod.add_url_rule(
    "/subject/<uuid:subject_id>",
    view_func=views.update_subject,
    methods=["PUT"],
)
mod.add_url_rule(
    "/subject/<uuid:subject_id>",
    view_func=views.update_subject,
    methods=["DELETE"],
)
