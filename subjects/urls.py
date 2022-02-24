from flask import Blueprint

from subjects import views
from users import urls as user_urls

general_mod = Blueprint("general_subject", __name__, url_prefix="/subjects")
general_mod_with_uuid = Blueprint(
    "general_subject_with_uuid", __name__, url_prefix="/<uuid:subject_id>"
)
general_mod.register_blueprint(general_mod_with_uuid)

mod = Blueprint("subject", __name__, url_prefix="/subjects")
mod_with_uuid = Blueprint(
    "subject_with_uuid", __name__, url_prefix="/<uuid:subject_id>"
)
mod.register_blueprint(mod_with_uuid)
user_urls.teacher_mod_with_uuid.register_blueprint(mod)
# /subjects
general_mod.add_url_rule("", view_func=views.get_subjects, methods=["GET"])

# /subjects/<subject_id>
general_mod_with_uuid.add_url_rule(
    "", view_func=views.get_subject, methods=["GET"]
)

# /users/teachers/<teacher_id>/subjects
mod.add_url_rule("/create", view_func=views.create_subject, methods=["POST"])
mod.add_url_rule("", view_func=views.get_teacher_subjects, methods=["GET"])

# /users/teachers/<teacher_id>/subjects/<subject_id>
mod_with_uuid.add_url_rule(
    "", view_func=views.get_teacher_subject, methods=["GET"]
)
mod_with_uuid.add_url_rule("", view_func=views.update_subject, methods=["PUT"])
mod_with_uuid.add_url_rule(
    "", view_func=views.delete_subject, methods=["DELETE"]
)
