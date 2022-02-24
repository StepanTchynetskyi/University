from flask import Blueprint

from users import views

mod = Blueprint("users", __name__, url_prefix="/users")

student_mod = Blueprint("students", __name__, url_prefix="/students")
student_mod_with_uuid = Blueprint(
    "student_mod_with_uuid", __name__, url_prefix="/<uuid:student_id>"
)
student_mod.register_blueprint(student_mod_with_uuid)

teacher_mod = Blueprint("teachers", __name__, url_prefix="/teachers")
teacher_mod_with_uuid = Blueprint(
    "teacher_with_uuid", __name__, url_prefix="/<uuid:teacher_id>"
)
teacher_mod.register_blueprint(teacher_mod_with_uuid)

mod.register_blueprint(student_mod)
mod.register_blueprint(teacher_mod)

# /users/students/create
student_mod.add_url_rule(
    "/create", view_func=views.create_student, methods=["POST"]
)

# /users/students/
student_mod.add_url_rule("", view_func=views.get_students, methods=["GET"])

# /users/students/<uuid:student_id>/
student_mod_with_uuid.add_url_rule(
    "",
    view_func=views.get_student,
    methods=["GET"],
)
student_mod_with_uuid.add_url_rule(
    "",
    view_func=views.update_student,
    methods=["PUT"],
)
student_mod_with_uuid.add_url_rule(
    "", view_func=views.soft_delete_student, methods=["DELETE"]
)

# /users/students/<uuid:student_id>/hard_delete
student_mod_with_uuid.add_url_rule(
    "/hard_delete", view_func=views.hard_delete_student, methods=["DELETE"]
)

# /users/teachers/create
teacher_mod.add_url_rule(
    "/create", view_func=views.create_teacher, methods=["POST"]
)

# /users/teachers/
teacher_mod.add_url_rule("/", view_func=views.get_teachers, methods=["GET"])

# /users/teachers/<uuid:teacher_id>
teacher_mod_with_uuid.add_url_rule(
    "/", view_func=views.get_teacher, methods=["GET"]
)
teacher_mod_with_uuid.add_url_rule(
    "/", view_func=views.update_teacher, methods=["PUT"]
)
teacher_mod_with_uuid.add_url_rule(
    "/", view_func=views.soft_delete_teacher, methods=["DELETE"]
)

# /users/teachers/<uuid:teacher_id>/hard_delete
teacher_mod_with_uuid.add_url_rule(
    "/hard_delete", view_func=views.hard_delete_teacher, methods=["DELETE"]
)

# /users/teachers/<uuid:teacher_id>/appoint-subjects/<uuid:subject_id>
teacher_mod_with_uuid.add_url_rule(
    "/appoint-subjects/<uuid:subject_id>",
    view_func=views.appoint_subject_to_teacher,
    methods=["POST"],
)

# /users/teachers/<uuid:teacher_id>/appoint-subjects-to-teacher
teacher_mod_with_uuid.add_url_rule(
    "/appoint-subjects-to-teacher",
    view_func=views.appoint_subjects_to_teacher,
    methods=["POST"],
)

# /users/teachers/<uuid:teacher_id>/appoint-student-to-group/groups/<uuid:group_id>
teacher_mod_with_uuid.add_url_rule(
    "/appoint-student-to-group/groups/<uuid:group_id>",
    view_func=views.appoint_student_to_group,
    methods=["POST"],
)

# /users/teachers/<uuid:teacher_id>/appoint-subjects-to-specialty/specialties/<uuid:specialty_id>
teacher_mod_with_uuid.add_url_rule(
    "/appoint-subjects-to-specialty/specialties/<uuid:specialty_id>",
    view_func=views.appoint_subject_to_specialty,
    methods=["POST"],
)

# /users/teachers/<uuid:teacher_id>/appoint-subject-to-group/groups/<uuid:group_id>
teacher_mod_with_uuid.add_url_rule(
    "/appoint-subject-to-group/groups/<uuid:group_id>",
    view_func=views.appoint_subject_to_group,
    methods=["POST"],
)

# /users/teachers/<uuid:teacher_id>/disappoint-subject/<uuid:subject_id>
teacher_mod_with_uuid.add_url_rule(
    "/disappoint-subject/<uuid:subject_id>",
    view_func=views.remove_subject_from_teacher,
    methods=["DELETE"],
)

# /users/teachers/<uuid:teacher_id>/disappoint-subjects-from-teacher
teacher_mod_with_uuid.add_url_rule(
    "/disappoint-subjects-from-teacher",
    view_func=views.remove_subjects_from_teacher,
    methods=["DELETE"],
)

# /users/teachers/<uuid:teacher_id>/disappoint-student-from-group/groups/<uuid:group_id>
teacher_mod_with_uuid.add_url_rule(
    "/disappoint-student-from-group/groups/<uuid:group_id>",
    view_func=views.remove_student_from_group,
    methods=["DELETE"],
)

# /users/teachers/<uuid:teacher_id>/disappoint-subjects-from-specialty/specialties/<uuid:specialty_id>
teacher_mod_with_uuid.add_url_rule(
    "/disappoint-subjects-from-specialty/specialties/<uuid:specialty_id>",
    view_func=views.remove_subject_from_specialty,
    methods=["DELETE"],
)

# /users/teachers/<uuid:teacher_id>/disappoint-subjects-from-group/groups/<uuid:group_id>
teacher_mod_with_uuid.add_url_rule(
    "/disappoint-subjects-from-group/groups/<uuid:group_id>",
    view_func=views.remove_subject_from_group,
    methods=["DELETE"],
)
