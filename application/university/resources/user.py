from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    jwt_required,
)

from application.blacklist import BLACKLIST
from application.university.schemas.user import (
    UserSchema,
    StudentSchema,
    TeacherSchema,
    LoginSchema,
)
from application.university.models.position import PositionModel
from application.university.models.user import (
    commit_specific_user,
    StudentModel,
    TeacherModel,
    UserModel,
)
from application.university.utils.custom_decorators import (
    find_active_user,
    process_user_json,
)
from application.university.utils.constants import (
    CREATED_SUCCESSFULLY,
    DOES_NOT_EXIST,
    UPDATED_SUCCESSFULLY,
    SUCCESSFULLY_DELETED,
    STUDENT,
    TEACHER,
    POSITION,
)
from application.university.utils.utils import (
    update_specific_user,
    check_password,
)

user_blprnt = Blueprint("users", __name__, url_prefix="/users")
auth_blprnt = Blueprint("auth", __name__, url_prefix="/auth")

user_schema = UserSchema()
student_schema = StudentSchema()
teacher_schema = TeacherSchema()
login_schema = LoginSchema()


@user_blprnt.route("/students/student/create", methods=["POST"])
@process_user_json(StudentModel, STUDENT, user_schema, request)
def create_student(student_json, user):
    student = student_schema.load(student_json)
    student.id = user.id
    commit_specific_user(user, student)
    student_json = student_schema.dump(student)
    return {
        "message": CREATED_SUCCESSFULLY.format(STUDENT, student.id),
        "data": student_json,
    }, 201


@user_blprnt.route("/students", methods=["GET"])
@jwt_required()
def get_students():
    students = [
        student_schema.dump(student)
        for student in StudentModel.get_all_records()
    ]
    return {"data": students}, 200


@user_blprnt.route("/students/student/<uuid:student_id>", methods=["GET"])
@find_active_user(StudentModel, STUDENT)
def get_student(student):
    return {"data": student_schema.dump(student)}, 200


@user_blprnt.route("/students/student/<uuid:student_id>", methods=["PUT"])
@find_active_user(StudentModel, STUDENT)
def update_student(student):
    student_json = update_specific_user(
        student, user_schema, student_schema, request
    )
    return {
        "message": UPDATED_SUCCESSFULLY.format(STUDENT, student.id),
        "data": student_json,
    }, 200


# TODO: should be deleted or allowed just for admin or user with the specified id
@user_blprnt.route(
    "/students/student/hard_delete/<uuid:student_id>", methods=["DELETE"]
)
@find_active_user(StudentModel, STUDENT)
def hard_delete_student(student):
    student.remove_from_db()
    return {"message": SUCCESSFULLY_DELETED.format(STUDENT, student.id)}, 200


@user_blprnt.route("/students/student/<uuid:student_id>", methods=["DELETE"])
@find_active_user(StudentModel, STUDENT)
def soft_delete_student(student):
    student.is_active = False
    student.save_to_db()
    return {"message": SUCCESSFULLY_DELETED.format(STUDENT, student.id)}, 200


@user_blprnt.route("/teachers/teacher/create", methods=["POST"])
@process_user_json(TeacherModel, TEACHER, user_schema, request)
def create_teacher(teacher_json, user):
    teacher = teacher_schema.load(teacher_json)
    position_id = teacher_json.get("position_id", None)
    position = PositionModel.get_by_id(position_id)
    if not position:
        return {"message": DOES_NOT_EXIST.format(POSITION, position_id)}, 400
    teacher.id = user.id
    commit_specific_user(user, teacher)
    teacher_json = teacher_schema.dump(teacher)
    return {
        "message": CREATED_SUCCESSFULLY.format(TEACHER, teacher.id),
        "data": teacher_json,
    }, 201


@user_blprnt.route("/teachers", methods=["GET"])
def get_teachers():
    teachers = [
        teacher_schema.dump(teacher)
        for teacher in TeacherModel.get_all_records()
    ]
    return {"data": teachers}, 200


@user_blprnt.route("/teachers/teacher/<uuid:teacher_id>", methods=["GET"])
@find_active_user(TeacherModel, TEACHER)
def get_teacher(teacher):
    return {"data": teacher_schema.dump(teacher)}, 200


@user_blprnt.route("/teachers/teacher/<uuid:teacher_id>", methods=["PUT"])
@find_active_user(TeacherModel, TEACHER)
def update_teacher(teacher):
    position_id = request.get_json().get("position_id", None)
    if position_id:
        position = PositionModel.get_by_id(position_id)
        if not position:
            return {
                "message": DOES_NOT_EXIST.format(POSITION, position.id)
            }, 400
    teacher_json = update_specific_user(
        teacher, user_schema, teacher_schema, request
    )
    return {
        "message": UPDATED_SUCCESSFULLY.format(STUDENT, teacher.id),
        "data": teacher_json,
    }, 200


@auth_blprnt.route("/login", methods=["POST"])
def login_user():
    user_json = request.get_json()
    loaded_user = login_schema.load(user_json)
    user = UserModel.get_by_email(loaded_user["email"])
    if user and check_password(loaded_user["password"], user.password):
        access_token = create_access_token(identity=user.id, fresh=True)
        refresh_token = create_refresh_token(user.id)
        return {
            "data": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": login_schema.dump(loaded_user),
            }
        }, 200


@auth_blprnt.route("/logout", methods=["POST"])
@jwt_required()
def logout_user():
    jti = get_jwt()["jti"]
    BLACKLIST.add(jti)
    return {"message": "Successfully logged out"}, 200


# TODO: should be deleted or allowed just for admin or user with the specified id
@user_blprnt.route(
    "/teachers/teacher/hard_delete/<uuid:teacher_id>", methods=["DELETE"]
)
@find_active_user(TeacherModel, TEACHER)
def hard_delete_teacher(teacher):
    teacher.remove_from_db()
    return {"message": SUCCESSFULLY_DELETED.format(TEACHER, teacher.id)}, 200


@user_blprnt.route("/teachers/teacher/<uuid:teacher_id>", methods=["DELETE"])
@find_active_user(TeacherModel, TEACHER)
def soft_delete_teacher(teacher):
    teacher.is_active = False
    teacher.save_to_db()
    return {"message": SUCCESSFULLY_DELETED.format(STUDENT, teacher.id)}, 200


@user_blprnt.route(
    "/teachers/teacher/<uuid:teacher_id>/appoint-subjects/appoint-subject/<uuid:subject_id>",
    methods=["POST"],
)
def appoint_subject_to_teacher(teacher_id, subject_id):
    return {"message: ": "TODO"}, 200


@user_blprnt.route(
    "/teachers/teacher/<uuid:teacher_id>/appoint-subjects/appoint-subjects",
    methods=["POST"],
)
def appoint_subjects_to_teacher(teacher_id):
    return {"message: ": "TODO"}, 200


@user_blprnt.route(
    "/students/student/<uuid:student_id>/appoint-groups/appoint-group/<uuid:group_id>",
    methods=["POST"],
)
def appoint_group_to_student(student_id, group_id):
    return {"message: ": "TODO"}, 200


@user_blprnt.route(
    "/students/student/<uuid:student_id>/appoint-groups", methods=["POST"]
)
def appoint_group_to_students(student_id):
    # TODO: add students from group, and students from list of UUIDs
    return {"message: ": "TODO"}, 200
