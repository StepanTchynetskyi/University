from flask import Blueprint

from users import views

mod = Blueprint("users", __name__, url_prefix="/users")

mod.add_url_rule(
    "/students/student/create",
    view_func=views.create_student,
    methods=["POST"],
)
mod.add_url_rule("/students", view_func=views.get_students, methods=["GET"])
mod.add_url_rule(
    "/students/student/<uuid:student_id>",
    view_func=views.get_student,
    methods=["GET"],
)
mod.add_url_rule(
    "/students/student/<uuid:student_id>",
    view_func=views.update_student,
    methods=["PUT"],
)
mod.add_url_rule(
    "/students/student/hard_delete/<uuid:student_id>",
    view_func=views.hard_delete_student,
    methods=["DELETE"],
)
mod.add_url_rule(
    "/students/student/<uuid:student_id>",
    view_func=views.soft_delete_student,
    methods=["DELETE"],
)
mod.add_url_rule(
    "/teachers/teacher/create",
    view_func=views.create_teacher,
    methods=["POST"],
)
mod.add_url_rule("/teachers", view_func=views.get_teachers, methods=["GET"])
mod.add_url_rule(
    "/teachers/teacher/<uuid:teacher_id>",
    view_func=views.get_teacher,
    methods=["GET"],
)
mod.add_url_rule(
    "/teachers/teacher/<uuid:teacher_id>",
    view_func=views.update_teacher,
    methods=["PUT"],
)
mod.add_url_rule(
    "/teachers/teacher/hard_delete/<uuid:teacher_id>",
    view_func=views.hard_delete_teacher,
    methods=["DELETE"],
)

mod.add_url_rule(
    "/teachers/teacher/<uuid:teacher_id>",
    view_func=views.soft_delete_teacher,
    methods=["DELETE"],
)

mod.add_url_rule(
    "/teachers/teacher/<uuid:teacher_id>/appoint-subjects/appoint-subject/subjects/subject/<uuid:subject_id>",
    view_func=views.appoint_subject_to_teacher,
    methods=["POST"],
)

mod.add_url_rule(
    "/teachers/teacher/<uuid:teacher_id>/appoint-subjects-to_teacher",
    view_func=views.appoint_subjects_to_teacher,
    methods=["POST"],
)

mod.add_url_rule(
    "/teachers/teacher/<uuid:teacher_id>/appoint-student-to-group/groups/group/<uuid:group_id>",
    view_func=views.appoint_student_to_group,
    methods=["POST"],
)

mod.add_url_rule(
    "/teachers/teacher/<uuid:teacher_id>/appoint-subjects-to-specialty/"
    "specialties/specialty/<uuid:specialty_id>",
    view_func=views.appoint_subject_to_specialty,
    methods=["POST"],
)

mod.add_url_rule(
    "/teachers/teacher/<uuid:teacher_id>/appoint-subject-to-group/groups/group/<uuid:group_id>",
    view_func=views.appoint_subject_to_group,
    methods=["POST"],
)

mod.add_url_rule(
    "/teachers/teacher/<uuid:teacher_id>/appoint-subjects/disappoint-subject/"
    "subjects/subject/<uuid:subject_id>",
    view_func=views.remove_subject_from_teacher,
    methods=["DELETE"],
)

mod.add_url_rule(
    "/teachers/teacher/<uuid:teacher_id>/disappoint-subjects-from-teacher",
    view_func=views.remove_subjects_from_teacher,
    methods=["DELETE"],
)

mod.add_url_rule(
    "/teachers/teacher/<uuid:teacher_id>/disappoint-student-from-group/groups/group/<uuid:group_id>",
    view_func=views.remove_student_from_group,
    methods=["DELETE"],
)

mod.add_url_rule(
    "/teachers/teacher/<uuid:teacher_id>/disappoint-subjects-from-specialty/"
    "specialties/specialty/<uuid:specialty_id>",
    view_func=views.remove_subject_from_specialty,
    methods=["DELETE"],
)

mod.add_url_rule(
    "/teachers/teacher/<uuid:teacher_id>/disappoint-subjects-from-group/groups/group/<uuid:group_id>",
    view_func=views.remove_subject_from_group,
    methods=["DELETE"],
)
