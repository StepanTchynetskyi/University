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
    StudentModel,
    save_to_db,
)
from application.university.utils.custom_exceptions import CreateUserException
from application.university.utils.constants import (
    PW_DO_NOT_MATCH,
    USER_CREATED_SUCCESSFULLY,
    POSITION_ID_NOT_PROVIDED,
    POSITION_DOES_NOT_EXIST,
    USER_NOT_FOUND_BY_ID,
    USER_UPDATED_SUCCESSFULLY,
    SUCCESSFULLY_DELETED,
    USER_ALREADY_EXIST,
    SOMETHING_WENT_WRONG,
)

user_blprnt = Blueprint("users", __name__, url_prefix="/users")

user_schema = UserSchema()
student_schema = StudentSchema()
teacher_schema = TeacherSchema()


def process_user_data():
    user_json = request.get_json()
    user = UserModel.get_by_email(user_json.get("email", None))
    if user:
        raise CreateUserException(USER_ALREADY_EXIST.format(user.email))
    if user_json["password"] != user_json.get("password1", None):
        raise CreateUserException(PW_DO_NOT_MATCH)
    user = user_schema.load(user_json)
    user.id = uuid.uuid4()
    return user_json, user


@user_blprnt.route("/students/student/create", methods=["POST"])
def create_student():
    try:
        processed_user = process_user_data()
    except CreateUserException as err:
        return {"message": str(err)}, 400
    user_json, user = processed_user
    student = student_schema.load(user_json)
    student.id = user.id
    commit_specific_user(user, student)
    return {
        "message": USER_CREATED_SUCCESSFULLY.format("Student", student.id)
    }, 201


@user_blprnt.route("/teacher/create", methods=["POST"])
def create_teacher():
    processed_user = process_user_data()
    if not processed_user:
        return {"message": PW_DO_NOT_MATCH}, 400
    user_json, user = processed_user
    position_id = user_json.get("position_id", None)
    if not position_id:
        return {"message": POSITION_ID_NOT_PROVIDED}, 400
    position = PositionModel.get_by_id(position_id)
    if not position:
        return {"message": POSITION_DOES_NOT_EXIST.format(position_id)}, 400
    teacher = teacher_schema.load(user_json)
    teacher.id = user.id
    commit_specific_user(user, teacher)
    return {
        "message": USER_CREATED_SUCCESSFULLY.format("Student", teacher.id)
    }, 201


@user_blprnt.route("/students", methods=["GET"])
def get_students():
    students = [
        student_schema.dump(student)
        for student in StudentModel.get_all_students()
    ]
    return jsonify(students), 200


@user_blprnt.route("/students/student/<uuid:student_id>", methods=["GET"])
def get_student(student_id):
    student = StudentModel.get_by_id(student_id)
    student = student_schema.dump(student)
    if student:
        return jsonify(student), 200
    return {"message": USER_NOT_FOUND_BY_ID.format(student_id)}, 400


@user_blprnt.route("/students/student/<uuid:student_id>", methods=["PUT"])
def update_student(student_id):
    student = StudentModel.get_by_id(student_id)
    if not student:
        return {"message": USER_NOT_FOUND_BY_ID.format(student_id)}, 400
    student_json = request.get_json()
    user_json = student_json.pop("user", None)

    if user_json:
        user = user_schema.load(user_json, instance=student.user, partial=True)
        student = student_schema.load(
            student_json, instance=student, partial=True
        )
        error = commit_specific_user(user, student)
    else:
        student = student_schema.load(
            student_json, instance=student, partial=True
        )
        error = save_to_db(student)
    if error:
        return {"message": SOMETHING_WENT_WRONG.format(error)}, 400
    return {"message": USER_UPDATED_SUCCESSFULLY.format(student_id)}, 200


@user_blprnt.route("/students/student/<uuid:student_id>", methods=["DELETE"])
def delete_student(student_id):
    student = StudentModel.get_by_id(student_id)
    if not student:
        return {"message": USER_NOT_FOUND_BY_ID.format(student_id)}, 400
    student.remove_from_db(student.user)
    return {"message": SUCCESSFULLY_DELETED.format(student_id)}, 200
