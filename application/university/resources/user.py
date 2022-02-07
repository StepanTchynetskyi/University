from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    jwt_required,
    get_jwt_identity,
)

from application import SubjectModel, GroupModel
from application.blacklist import BLACKLIST
from application.university.schemas.group import GroupSchema
from application.university.schemas.user import (
    UserSchema,
    StudentSchema,
    TeacherSchema,
    LoginSchema,
)
from application.university.models.position import PositionModel
from application.university.models.user import (
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
    PERMISSION_DENIED,
    APPOINT_ITEM,
    ITEM_NOT_PROVIDED,
    SUBJECT,
    NOT_FOUND_BY_ID,
    GROUP,
)
from application.university.utils.utils import (
    update_specific_user,
    check_password,
    process_many_to_many_insert,
)
from application.university.utils.custom_exceptions import (
    SearchException,
    NotProvided,
)

user_blprnt = Blueprint("users", __name__, url_prefix="/users")
auth_blprnt = Blueprint("auth", __name__, url_prefix="/auth")

user_schema = UserSchema()
student_schema = StudentSchema()
teacher_schema = TeacherSchema()
login_schema = LoginSchema()
group_schema = GroupSchema()


@user_blprnt.route("/students/student/create", methods=["POST"])
@process_user_json(student_schema, STUDENT, request)
def create_student(student):
    student_json = student_schema.dump(student)
    return {
        "message": CREATED_SUCCESSFULLY.format(STUDENT, student.id),
        "data": student_json,
    }, 201


@user_blprnt.route("/students", methods=["GET"])
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
@jwt_required()
@find_active_user(StudentModel, STUDENT)
def update_student(student):
    student_json = update_specific_user(student, student_schema, request)
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
@process_user_json(teacher_schema, TEACHER, request)
def create_teacher(teacher):
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
@jwt_required()
@find_active_user(TeacherModel, TEACHER)
def update_teacher(teacher):
    position_id = request.get_json().get("position_id", None)
    if position_id:
        position = PositionModel.get_by_id(position_id)
        if not position:
            return {
                "message": DOES_NOT_EXIST.format(POSITION, position.id)
            }, 400
    teacher_json = update_specific_user(teacher, teacher_schema, request)
    return {
        "message": UPDATED_SUCCESSFULLY.format(STUDENT, teacher.id),
        "data": teacher_json,
    }, 200


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


@auth_blprnt.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity, fresh=False)
    return {"data": {"access_token": access_token}}


@user_blprnt.route(
    "/teachers/teacher/<uuid:teacher_id>/appoint-subjects/appoint-subject/<uuid:subject_id>",
    methods=["POST"],
)
@jwt_required()
@find_active_user(TeacherModel, TEACHER, check_jwt=True)
def appoint_subject_to_teacher(teacher, subject_id):
    subject = SubjectModel.get_by_id(subject_id)
    if not subject:
        raise SearchException("Subject not found", status_code=400)
    teacher.subjects.append(subject)
    teacher.save_to_db()
    teacher_json = teacher_schema.dump(teacher)
    return {
        "message": APPOINT_ITEM.format(subject.name, teacher.first_name),
        "data": teacher_json,
    }, 200


@user_blprnt.route(
    "/teachers/teacher/<uuid:teacher_id>/appoint-subjects",
    methods=["POST"],
)
@jwt_required()
@find_active_user(TeacherModel, TEACHER, check_jwt=True)
def appoint_subjects_to_teacher(teacher):
    data = request.get_json()
    teacher_json, subject_ids = process_many_to_many_insert(
        teacher, teacher_schema, SUBJECT, data, SubjectModel
    )
    return {
        "message": APPOINT_ITEM.format(subject_ids, teacher.first_name),
        "data": teacher_json,
    }, 200


# @user_blprnt.route(
#     "/students/student/<uuid:student_id>/appoint-groups/appoint-group/<uuid:group_id>",
#     methods=["POST"],
# )
# def appoint_group_to_student(student_id, group_id):
#     return {"message: ": "TODO"}, 200


@user_blprnt.route(
    "/teachers/teacher/<uuid:teacher_id>/appoint-student-to-group",
    methods=["POST"],
)
@jwt_required()
@find_active_user(TeacherModel, TEACHER, check_jwt=True)
def appoint_student_to_group(teacher):
    data = request.get_json()
    group_id = data.get("group_id", None)
    if not group_id:
        raise NotProvided(ITEM_NOT_PROVIDED.format(GROUP))
    group = GroupModel.get_by_id(group_id)
    if not group:
        raise SearchException(NOT_FOUND_BY_ID.format(GROUP, group_id))
    if group.curator_id == teacher.id:
        raise PermissionError(
            PERMISSION_DENIED.format(str(teacher.id))
        )  # message should be changed
    group_json, student_ids = process_many_to_many_insert(
        group, group_schema, STUDENT, data, StudentModel
    )
    return {
        "message": APPOINT_ITEM.format(student_ids, group.name),
        "data": group_json,
    }, 200
