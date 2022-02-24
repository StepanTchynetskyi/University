from flask import Blueprint

from assignments import views
from subjects import urls as subject_urls


mod = Blueprint("assignment", __name__, url_prefix="/assignments")
mod_with_uuid = Blueprint(
    "assignment_with_uuid", __name__, url_prefix="/<uuid:assignment_id>"
)
mod.register_blueprint(mod_with_uuid)
subject_urls.mod_with_uuid.register_blueprint(mod)
general_mod = Blueprint(
    "assignment",
    __name__,
    url_prefix="/subjects/<uuid:subject_id>/assignments",
)
general_mode_with_uuid = Blueprint(
    "assignment", __name__, url_prefix="/<uuid:assignment_id>"
)
general_mod.register_blueprint(general_mode_with_uuid)


#  /subjects/<uuid:subject_id>/assignments
general_mod.add_url_rule("", view_func=views.get_assignments, methods=["GET"])

# /users/teachers/<uuid:teacher_id>/subjects/<uuid:subject_id>/assignments/create
mod.add_url_rule(
    "/create", view_func=views.create_assignment, methods=["POST"]
)

#  /subjects/<uuid:subject_id>/assignments/<uuid:assignment_id>
general_mode_with_uuid.add_url_rule(
    "", view_func=views.get_assignment, methods=["GET"]
)

#  /users/teachers/<uuid:teacher_id>/subjects/<uuid:subject_id>/assignments/<uuid:assignment_id>
mod_with_uuid.add_url_rule(
    "", view_func=views.update_assignment, methods=["PUT"]
)
mod_with_uuid.add_url_rule(
    "", view_func=views.delete_assignment, methods=["DELETE"]
)
