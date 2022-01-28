import uuid
from flask import jsonify, Blueprint, request

from application.university.schemas.user import (
    UserSchema,
    StudentSchema,
    TeacherSchema,
    UserModel,
)
from application.university.models.position import PositionModel
from application.university.models.user import (
    commit_specific_user,
    save_to_db,
    StudentModel,
    TeacherModel,
)
from application.university.utils.custom_exceptions import (
    CreateUserException,
    UserSearchException,
)
from application.university.utils.constants import (
    PW_DO_NOT_MATCH,
    CREATED_SUCCESSFULLY,
    POSITION_DOES_NOT_EXIST,
    NOT_FOUND_BY_ID,
    UPDATED_SUCCESSFULLY,
    SUCCESSFULLY_DELETED,
    ALREADY_EXIST,
    SOMETHING_WENT_WRONG,
    NOT_ACTIVE_USER,
    STUDENT,
    TEACHER,
)

user_blprnt = Blueprint("users", __name__, url_prefix="/users")

user_schema = UserSchema()
student_schema = StudentSchema()
teacher_schema = TeacherSchema()


def process_user_data(specific_user_model, user_type):
    user_json = request.get_json()
    if user_json["password"] != user_json.get("password1", None):
        raise CreateUserException(PW_DO_NOT_MATCH)
    user = UserModel.get_by_email(user_json.get("email", None))
    if user:
        specific_user = specific_user_model.get_by_id(user.id)
        if specific_user:
            raise CreateUserException(
                ALREADY_EXIST.format(user_type, user.email)
            )
    else:
        user = user_schema.load(user_json)
        user.id = uuid.uuid4()
    return user_json, user


def process_specific_user(user_id, specific_model, user_type):
    specific_user = specific_model.get_by_id(user_id)
    if not specific_user:
        raise UserSearchException(
            message=NOT_FOUND_BY_ID.format(user_type, user_id), status_code=400
        )
    if not specific_user.is_active:
        raise UserSearchException(
            message=NOT_ACTIVE_USER.format(user_id), status_code=400
        )
    return specific_user


def update_specific_user(specific_user, specific_schema):
    specific_user_json = request.get_json()
    user_json = specific_user_json.pop("user", None)

    if user_json:
        user = user_schema.load(
            user_json, instance=specific_user.user, partial=True
        )
        student = specific_schema.load(
            specific_user_json, instance=specific_user, partial=True
        )
        error = commit_specific_user(user, student)
    else:
        student = specific_schema.load(
            specific_user_json, instance=specific_user, partial=True
        )
        error = save_to_db(student)
    return error


@user_blprnt.route("/students/student/create", methods=["POST"])
def create_student():
    try:
        processed_user = process_user_data(StudentModel, STUDENT)
    except CreateUserException as err:
        return {"message": str(err)}, 400
    user_json, user = processed_user
    student = student_schema.load(user_json)
    student.id = user.id
    commit_specific_user(user, student)
    return {"message": CREATED_SUCCESSFULLY.format("Student", student.id)}, 201


@user_blprnt.route("/students", methods=["GET"])
def get_students():
    students = [
        student_schema.dump(student)
        for student in StudentModel.get_all_students()
    ]
    return jsonify(students), 200


@user_blprnt.route("/students/student/<uuid:student_id>", methods=["GET"])
def get_student(student_id):
    try:
        student = process_specific_user(student_id, StudentModel, STUDENT)
    except UserSearchException as err:
        return {"message": str(err)}, err.status_code
    return jsonify(student_schema.dump(student)), 200


@user_blprnt.route("/students/student/<uuid:student_id>", methods=["PUT"])
def update_student(student_id):
    try:
        student = process_specific_user(student_id, StudentModel, STUDENT)
    except UserSearchException as err:
        return {"message": str(err)}, err.status_code
    error = update_specific_user(student, student_schema)
    if error:
        return {"message": SOMETHING_WENT_WRONG.format(error)}, 400
    return {"message": UPDATED_SUCCESSFULLY.format(STUDENT, student_id)}, 200


# TODO: should be deleted or allowed just for admin or user with the specified id
@user_blprnt.route(
    "/students/student/hard_delete/<uuid:student_id>", methods=["DELETE"]
)
def hard_delete_student(student_id):
    student = StudentModel.get_by_id(student_id)
    if not student:
        return {"message": NOT_FOUND_BY_ID.format(STUDENT, student_id)}, 400
    student.remove_from_db()
    return {"message": SUCCESSFULLY_DELETED.format(STUDENT, student_id)}, 200


@user_blprnt.route("/students/student/<uuid:student_id>", methods=["DELETE"])
def soft_delete_student(student_id):
    try:
        student = process_specific_user(student_id, StudentModel, STUDENT)
    except UserSearchException as err:
        return {"message": str(err)}, err.status_code
    student.is_active = False
    error = save_to_db(student.user)
    if error:
        return {"message": SOMETHING_WENT_WRONG.format(error)}, 400
    return {"message": SUCCESSFULLY_DELETED.format(STUDENT, student_id)}, 200


@user_blprnt.route("/teachers/teacher/create", methods=["POST"])
def create_teacher():
    try:
        processed_user = process_user_data(TeacherModel, TEACHER)
    except CreateUserException as err:
        return {"message": str(err)}, 400
    user_json, user = processed_user
    teacher = teacher_schema.load(user_json)
    position_id = user_json.get("position_id", None)
    position = PositionModel.get_by_id(position_id)
    if not position:
        return {"message": POSITION_DOES_NOT_EXIST.format(position_id)}, 400
    teacher.id = user.id
    error = commit_specific_user(user, teacher)
    if error:
        return {"message": SOMETHING_WENT_WRONG.format(error)}, 400
    return {"message": CREATED_SUCCESSFULLY.format(TEACHER, teacher.id)}, 201


@user_blprnt.route("/teachers", methods=["GET"])
def get_teachers():
    teachers = [
        teacher_schema.dump(teacher)
        for teacher in TeacherModel.get_all_teachers()
    ]
    return jsonify(teachers), 200


@user_blprnt.route("/teachers/teacher/<uuid:teacher_id>", methods=["GET"])
def get_teacher(teacher_id):
    try:
        teacher = process_specific_user(teacher_id, TeacherModel, TEACHER)
    except UserSearchException as err:
        return {"message": str(err)}, err.status_code
    return {"message": teacher_schema.dump(teacher)}, 200


@user_blprnt.route("/teachers/teacher/<uuid:teacher_id>", methods=["PUT"])
def update_teacher(teacher_id):
    try:
        teacher = process_specific_user(teacher_id, TeacherModel, TEACHER)
    except UserSearchException as err:
        return {"message": str(err)}, err.status_code
    position_id = request.get_json().get("position_id", None)
    if position_id:
        position = PositionModel.get_by_id(position_id)
        if not position:
            return {
                "message": POSITION_DOES_NOT_EXIST.format(position.id)
            }, 400
    error = update_specific_user(teacher, teacher_schema)
    if error:
        return {"message": SOMETHING_WENT_WRONG.format(error)}, 400
    return {"message": UPDATED_SUCCESSFULLY.format(STUDENT, teacher_id)}, 200


# TODO: should be deleted or allowed just for admin or user with the specified id
@user_blprnt.route(
    "/teachers/teacher/hard_delete/<uuid:teacher_id>", methods=["DELETE"]
)
def hard_delete_teacher(teacher_id):
    teacher = TeacherModel.get_by_id(teacher_id)
    if not teacher:
        return {"message": NOT_FOUND_BY_ID.format(TEACHER, teacher_id)}, 400
    teacher.remove_from_db()
    return {"message": SUCCESSFULLY_DELETED.format(TEACHER, teacher_id)}, 200


@user_blprnt.route("/teachers/teacher/<uuid:teacher_id>", methods=["DELETE"])
def soft_delete_teacher(teacher_id):
    try:
        teacher = process_specific_user(teacher_id, TeacherModel, TEACHER)
    except UserSearchException as err:
        return {"message": str(err)}, err.status_code
    teacher.is_active = False
    error = save_to_db(teacher.user)
    if error:
        return {"message": SOMETHING_WENT_WRONG.format(error)}, 400
    return {"message": SUCCESSFULLY_DELETED.format(STUDENT, teacher_id)}, 200
