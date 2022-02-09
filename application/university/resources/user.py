from typing import Tuple, Dict, Any
from uuid import UUID

from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    jwt_required,
    get_jwt_identity,
)
from application import SubjectModel, GroupModel, SpecialtyModel
from application.blacklist import BLACKLIST
from application.university.schemas.group import GroupSchema
from application.university.schemas.specialty import SpecialtySchema
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
    APPOINT_ITEM,
    SUBJECT,
    GROUP,
    SPECIALTY,
    EMAIL_DOES_NOT_EXISTS,
    PW_DO_NOT_MATCH,
)
from application.university.utils.utils import (
    update_specific_user,
    check_password,
    process_many_to_many_insert,
    process_entity_with_teacher,
)
from application.university.utils.custom_exceptions import (
    SearchException,
    InvalidCredentials,
)

user_blprnt = Blueprint("users", __name__, url_prefix="/users")
auth_blprnt = Blueprint("auth", __name__, url_prefix="/auth")

user_schema = UserSchema()
student_schema = StudentSchema()
teacher_schema = TeacherSchema()
login_schema = LoginSchema()
group_schema = GroupSchema()
specialty_schema = SpecialtySchema()


@user_blprnt.route("/students/student/create", methods=["POST"])
@process_user_json(student_schema, STUDENT, request)
def create_student(student: StudentModel) -> Tuple[Dict[str, Any], int]:
    """Creates Student account

    :param student: an object of existing student,
     received from @find_active_user by a UUID from url
    :type student: StudentModel
    :return: Tuple with a dictionary that contains 'message',
     "data" of the teacher and status code for the Response
    """
    student_json = student_schema.dump(student)
    return {
        "message": CREATED_SUCCESSFULLY.format(STUDENT, student.id),
        "data": student_json,
    }, 201


@user_blprnt.route("/students", methods=["GET"])
def get_students():
    """Shows active students and their data

    :return: Tuple with a dictionary that contains "data" of the teachers
     and status code for the Response
    """
    students = [
        student_schema.dump(student)
        for student in StudentModel.get_all_records()
    ]
    return {"data": students}, 200


@user_blprnt.route("/students/student/<uuid:student_id>", methods=["GET"])
@find_active_user(StudentModel, STUDENT)
def get_student(student: StudentModel) -> Tuple[Dict[str, Any], int]:
    """Shows specific student data

    :param student: an object of existing student,
     received from @find_active_user by a UUID from url
    :type student: StudentModel
    :return: Tuple with a dictionary that contains "data" of the teacher
     and status code for the Response
    """
    return {"data": student_schema.dump(student)}, 200


@user_blprnt.route("/students/student/<uuid:student_id>", methods=["PUT"])
@jwt_required(fresh=True)
@find_active_user(StudentModel, STUDENT, check_jwt=True)
def update_student(student: StudentModel) -> Tuple[Dict[str, Any], int]:
    """Opportunity for the Student to update account

    :param student: an object of existing student,
     received from @find_active_user by a UUID from url
    :type student: StudentModel
    :return: Tuple with a dictionary that contains 'message',
     "data" of the teacher and status code for the Response
    """
    student_json = update_specific_user(student, student_schema, request)
    return {
        "message": UPDATED_SUCCESSFULLY.format(STUDENT, student.id),
        "data": student_json,
    }, 200


# TODO: should be deleted or allowed just for admin or user with the specified id
@user_blprnt.route(
    "/students/student/hard_delete/<uuid:student_id>", methods=["DELETE"]
)
@jwt_required(fresh=True)
@find_active_user(StudentModel, STUDENT, check_jwt=True)
def hard_delete_student(student: StudentModel) -> Tuple[Dict[str, Any], int]:
    """Opportunity for the Student to delete account

    :param student: an object of existing student,
     received from @find_active_user by a UUID from url
    :type student: StudentModel
    :return: Tuple with a dictionary that contains "message" and status code
    """
    student.remove_from_db()
    return {"message": SUCCESSFULLY_DELETED.format(STUDENT, student.id)}, 200


@user_blprnt.route("/students/student/<uuid:student_id>", methods=["DELETE"])
@jwt_required(fresh=True)
@find_active_user(StudentModel, STUDENT, check_jwt=True)
def soft_delete_student(student: StudentModel) -> Tuple[Dict[str, Any], int]:
    """Opportunity for the Student to softly delete account

    :param student: an object of existing student,
     received from @find_active_user by a UUID from url
    :type student: StudentModel
    :return: Tuple with a dictionary that contains "message" and status code
    """
    student.is_active = False
    student.save_to_db()
    return {"message": SUCCESSFULLY_DELETED.format(STUDENT, student.id)}, 200


@user_blprnt.route("/teachers/teacher/create", methods=["POST"])
@process_user_json(teacher_schema, TEACHER, request)
def create_teacher(teacher: TeacherModel) -> Tuple[Dict[str, Any], int]:
    """Creates Teacher account

    :param teacher: an object of existing teacher,
     received from @find_active_user by a UUID from url
    :type teacher: TeacherModel
    :return: Tuple with a dictionary that contains 'message',
     "data" of the teacher and status code for the Response
    """
    teacher_json = teacher_schema.dump(teacher)
    return {
        "message": CREATED_SUCCESSFULLY.format(TEACHER, teacher.id),
        "data": teacher_json,
    }, 201


@user_blprnt.route("/teachers", methods=["GET"])
def get_teachers() -> Tuple[Dict[str, Any], int]:
    """Shows active teachers and their data

    :return: Tuple with a dictionary that contains "data" of the teachers
     and status code for the Response
    """
    teachers = [
        teacher_schema.dump(teacher)
        for teacher in TeacherModel.get_all_records()
    ]
    return {"data": teachers}, 200


@user_blprnt.route("/teachers/teacher/<uuid:teacher_id>", methods=["GET"])
@find_active_user(TeacherModel, TEACHER)
def get_teacher(teacher: TeacherModel) -> Tuple[Dict[str, Any], int]:
    """Shows specific teacher data

    :param teacher: an object of existing teacher,
     received from @find_active_user by a UUID from url
    :type teacher: TeacherModel
    :return: Tuple with a dictionary that contains "data" of the teacher
     and status code for the Response
    """
    return {"data": teacher_schema.dump(teacher)}, 200


@user_blprnt.route("/teachers/teacher/<uuid:teacher_id>", methods=["PUT"])
@jwt_required(fresh=True)
@find_active_user(TeacherModel, TEACHER, check_jwt=True)
def update_teacher(teacher: TeacherModel) -> Tuple[Dict[str, Any], int]:
    """Opportunity for the Teacher to update account

    :param teacher: an object of existing teacher,
     received from @find_active_user by a UUID from url
    :type teacher: TeacherModel
    :return: Tuple with a dictionary that contains 'message',
     "data" of the teacher and status code for the Response
    """
    position_id = request.get_json().get("position_id", None)
    if position_id:
        position = PositionModel.get_by_id(position_id)
        if not position:
            raise SearchException(DOES_NOT_EXIST.format(POSITION, position_id))
    teacher_json = update_specific_user(teacher, teacher_schema, request)
    return {
        "message": UPDATED_SUCCESSFULLY.format(TEACHER, teacher.id),
        "data": teacher_json,
    }, 200


# TODO: should be deleted or allowed just for admin or user with the specified id
@user_blprnt.route(
    "/teachers/teacher/hard_delete/<uuid:teacher_id>", methods=["DELETE"]
)
@jwt_required(fresh=True)
@find_active_user(TeacherModel, TEACHER, check_jwt=True)
def hard_delete_teacher(teacher: TeacherModel) -> Tuple[Dict[str, Any], int]:
    """Opportunity for the Teacher to delete account

    :param teacher: an object of existing teacher,
     received from @find_active_user by a UUID from url
    :type teacher: TeacherModel
    :return: Tuple with a dictionary that contains "message" and status code
    """
    teacher.remove_from_db()
    return {"message": SUCCESSFULLY_DELETED.format(TEACHER, teacher.id)}, 200


@user_blprnt.route("/teachers/teacher/<uuid:teacher_id>", methods=["DELETE"])
@jwt_required(fresh=True)
@find_active_user(TeacherModel, TEACHER, check_jwt=True)
def soft_delete_teacher(teacher: TeacherModel) -> Tuple[Dict[str, Any], int]:
    """Opportunity for the Teacher to softly delete account

    :param teacher: an object of existing teacher,
     received from @find_active_user by a UUID from url
    :type teacher: TeacherModel
    :return: Tuple with a dictionary that contains "message" and status code
    """
    teacher.is_active = False
    teacher.save_to_db()
    return {"message": SUCCESSFULLY_DELETED.format(TEACHER, teacher.id)}, 200


@auth_blprnt.route("/login", methods=["POST"])
def login_user() -> Tuple[Dict[str, Any], int]:
    """Log in user to the system with email and password

    :return: Tuple with a dictionary that contains "data" with
     'access_token', 'refresh_token', 'user_email' and status code
    """

    user_json = request.get_json()
    loaded_user = login_schema.load(user_json)
    user = UserModel.get_by_email(loaded_user["email"])
    if not user:
        raise SearchException(
            EMAIL_DOES_NOT_EXISTS.format(loaded_user["email"])
        )
    if not check_password(loaded_user["password"], user.password):
        raise InvalidCredentials(PW_DO_NOT_MATCH)
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
def logout_user() -> Tuple[Dict[str, Any], int]:
    """Logout user from the system, adding access_token to the BLACKLIST

    :return: Tuple with a dictionary that contains "status message" and status code
    """
    jti = get_jwt()["jti"]
    BLACKLIST.add(jti)
    return {"message": "Successfully logged out"}, 200


@auth_blprnt.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh() -> Tuple[Dict[str, Any], int]:
    """Refreshes expired access_token for User

    :return: Tuple with a dictionary that contains "data" with
     the access token for the User
    """
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity, fresh=False)
    return {"data": {"access_token": access_token}}, 200


@user_blprnt.route(
    "/teachers/teacher/<uuid:teacher_id>/appoint-subjects/appoint-subject/subjects/subject/<uuid:subject_id>",
    methods=["POST"],
)
@jwt_required()
@find_active_user(TeacherModel, TEACHER, check_jwt=True)
def appoint_subject_to_teacher(
    teacher: TeacherModel, subject_id: UUID
) -> Tuple[Dict[str, Any], int]:
    """Opportunity for the Teacher to appoint specific subjects

    :param teacher: an object of existing teacher,
     received from @find_active_user by a UUID from url
    :type teacher: TeacherModel
    :param subject_id: UUID of Subject from url
    :type subject_id: UUID
    :return: Tuple with a dictionary that contains 'message',
     "data" of the appointed items and status code for the Response
    """
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
    "/teachers/teacher/<uuid:teacher_id>/appoint-subjects-to_teacher",
    methods=["POST"],
)
@jwt_required()
@find_active_user(TeacherModel, TEACHER, check_jwt=True)
def appoint_subjects_to_teacher(
    teacher: TeacherModel,
) -> Tuple[Dict[str, Any], int]:
    """Opportunity for the Teacher to appoint subjects

    :param teacher: an object of existing teacher,
     received from @find_active_user by a UUID from url
    :type teacher: TeacherModel
    :return: Tuple with a dictionary that contains 'message',
     "data" of the appointed items and status code for the Response
    """
    data = request.get_json()
    subject_ids = data.get("subject_ids", None)
    teacher_json = process_many_to_many_insert(
        teacher, teacher_schema, SUBJECT, subject_ids, SubjectModel
    )
    return {
        "message": APPOINT_ITEM.format(subject_ids, teacher.first_name),
        "data": teacher_json,
    }, 200


@user_blprnt.route(
    "/teachers/teacher/<uuid:teacher_id>/appoint-student-to-group/groups/group/<uuid:group_id>",
    methods=["POST"],
)
@jwt_required()
@find_active_user(TeacherModel, TEACHER, check_jwt=True)
def appoint_student_to_group(
    teacher: TeacherModel, group_id: UUID
) -> Tuple[Dict[str, Any], int]:
    """Opportunity for the Curator of group to appoint students

    :param teacher: an object of existing teacher,
     received from @find_active_user by a UUID from url
    :type teacher: TeacherModel
    :param group_id: UUID of Specialty from url
    :type group_id: UUID
    :return: Tuple with a dictionary that contains 'message' and
     "data" of the appointed items and status code for the Response
    """
    data = request.get_json()
    student_ids = data.get("student_ids", None)
    group = process_entity_with_teacher(teacher, group_id, GroupModel, GROUP)
    group_json = process_many_to_many_insert(
        group, group_schema, STUDENT, student_ids, StudentModel
    )
    return {
        "message": APPOINT_ITEM.format(student_ids, group.name),
        "data": group_json,
    }, 200


@user_blprnt.route(
    "/teachers/teacher/<uuid:teacher_id>/appoint-subjects-to-specialty/"
    "specialties/specialty/<uuid:specialty_id>",
    methods=["POST"],
)
@jwt_required()
@find_active_user(TeacherModel, TEACHER, check_jwt=True)
def appoint_subject_to_specialty(
    teacher: TeacherModel, specialty_id: UUID
) -> Tuple[Dict[str, Any], int]:
    """Opportunity for the Head Teacher of specialty to appoint subjects

    :param teacher: an object of existing teacher,
     received from @find_active_user by a UUID from url
    :type teacher: TeacherModel
    :param specialty_id: UUID of Specialty from url
    :type specialty_id: UUID
    :return: Tuple with a dictionary that contains 'message' and
     "data" of the appointed items and status code for the Response
    """
    data = request.get_json()
    subject_ids = data.get("subject_ids", None)
    specialty = process_entity_with_teacher(
        teacher, specialty_id, SpecialtyModel, SPECIALTY
    )
    specialty_json = process_many_to_many_insert(
        specialty, specialty_schema, SUBJECT, subject_ids, SubjectModel
    )
    return {
        "message": APPOINT_ITEM.format(subject_ids, specialty.name),
        "data": specialty_json,
    }, 200


@user_blprnt.route(
    "/teachers/teacher/<uuid:teacher_id>/appoint-subject-to-group/groups/group/<uuid:group_id>",
    methods=["POST"],
)
@jwt_required()
@find_active_user(TeacherModel, TEACHER, check_jwt=True)
def appoint_subject_to_group(
    teacher: TeacherModel, group_id: UUID
) -> Tuple[Dict[str, Any], int]:
    data = request.get_json()
    subject_ids = data.get("subject_ids", None)
    group = process_entity_with_teacher(teacher, group_id, GroupModel, GROUP)
    group_json = process_many_to_many_insert(
        group, group_schema, SUBJECT, subject_ids, SubjectModel
    )
    return {
        "message": APPOINT_ITEM.format(subject_ids, group.name),
        "data": group_json,
    }, 200
