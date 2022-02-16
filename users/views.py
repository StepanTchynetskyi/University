from typing import Tuple, Dict, Any
from uuid import UUID

from flask import request
from flask_jwt_extended import jwt_required
from subjects.models import SubjectModel
from groups.models import GroupModel
from specialties.models import SpecialtyModel
from groups.schemas import GroupSchema
from specialties.schemas import SpecialtySchema
from users.schemas import (
    UserSchema,
    StudentSchema,
    TeacherSchema,
)
from positions.models import PositionModel
from users.models import (
    StudentModel,
    TeacherModel,
)
from utils.custom_decorators import (
    find_active_user,
)
from utils.constants import (
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
    NOT_FOUND_BY_ID,
    DATA_NOT_PROVIDED,
)
from utils.utils import (
    get_entity_with_teacher,
)
from utils.custom_exceptions import (
    SearchException,
    NotProvided,
)
from users.utils.utils import get_items, update_specific_user
from users.utils.custom_decorators import process_user_json


user_schema = UserSchema()
student_schema = StudentSchema()
teacher_schema = TeacherSchema()
group_schema = GroupSchema()
specialty_schema = SpecialtySchema()


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


@jwt_required(fresh=True)
@find_active_user(StudentModel, STUDENT, check_jwt=True)
def update_student(student: StudentModel) -> Tuple[Dict[str, Any], int]:
    """Allow the Student to update account

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
@jwt_required(fresh=True)
@find_active_user(StudentModel, STUDENT, check_jwt=True)
def hard_delete_student(student: StudentModel) -> Tuple[Dict[str, Any], int]:
    """Allow the Student to delete account

    :param student: an object of existing student,
     received from @find_active_user by a UUID from url
    :type student: StudentModel
    :return: Tuple with a dictionary that contains "message" and status code
    """
    student.remove_from_db()
    return {"message": SUCCESSFULLY_DELETED.format(STUDENT, student.id)}, 200


@jwt_required(fresh=True)
@find_active_user(StudentModel, STUDENT, check_jwt=True)
def soft_delete_student(student: StudentModel) -> Tuple[Dict[str, Any], int]:
    """Allow the Student to softly delete account

    :param student: an object of existing student,
     received from @find_active_user by a UUID from url
    :type student: StudentModel
    :return: Tuple with a dictionary that contains "message" and status code
    """
    student.is_active = False
    student.save_to_db()
    return {"message": SUCCESSFULLY_DELETED.format(STUDENT, student.id)}, 200


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


@jwt_required(fresh=True)
@find_active_user(TeacherModel, TEACHER, check_jwt=True)
def update_teacher(teacher: TeacherModel) -> Tuple[Dict[str, Any], int]:
    """Allow the Teacher to update account

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


@jwt_required(fresh=True)
@find_active_user(TeacherModel, TEACHER, check_jwt=True)
def hard_delete_teacher(teacher: TeacherModel) -> Tuple[Dict[str, Any], int]:
    """Allow the Teacher to delete account

    :param teacher: an object of existing teacher,
     received from @find_active_user by a UUID from url
    :type teacher: TeacherModel
    :return: Tuple with a dictionary that contains "message" and status code
    """
    teacher.remove_from_db()
    return {"message": SUCCESSFULLY_DELETED.format(TEACHER, teacher.id)}, 200


@jwt_required(fresh=True)
@find_active_user(TeacherModel, TEACHER, check_jwt=True)
def soft_delete_teacher(teacher: TeacherModel) -> Tuple[Dict[str, Any], int]:
    """Allow the Teacher to softly delete account

    :param teacher: an object of existing teacher,
     received from @find_active_user by a UUID from url
    :type teacher: TeacherModel
    :return: Tuple with a dictionary that contains "message" and status code
    """
    teacher.is_active = False
    teacher.save_to_db()
    return {"message": SUCCESSFULLY_DELETED.format(TEACHER, teacher.id)}, 200


@jwt_required()
@find_active_user(TeacherModel, TEACHER, check_jwt=True)
def appoint_subject_to_teacher(
    teacher: TeacherModel, subject_id: UUID
) -> Tuple[Dict[str, Any], int]:
    """Allow the Teacher to appoint specific subjects

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
        raise SearchException(
            NOT_FOUND_BY_ID.format(SUBJECT, subject_id), status_code=400
        )
    teacher.subjects.append(subject)
    teacher.save_to_db()
    teacher_json = teacher_schema.dump(teacher)
    return {
        "message": APPOINT_ITEM.format(subject.name, teacher.first_name),
        "data": teacher_json,
    }, 200


@jwt_required()
@find_active_user(TeacherModel, TEACHER, check_jwt=True)
def appoint_subjects_to_teacher(
    teacher: TeacherModel,
) -> Tuple[Dict[str, Any], int]:
    """Allow the Teacher to appoint subjects

    :param teacher: an object of existing teacher,
     received from @find_active_user by a UUID from url
    :type teacher: TeacherModel
    :return: Tuple with a dictionary that contains 'message',
     "data" of the appointed items and status code for the Response
    """
    data = request.get_json()
    subject_ids = data.get("subject_ids", None)
    subjects = get_items(SUBJECT, subject_ids, SubjectModel)
    teacher.subjects.extend(subjects)
    teacher.save_to_db()
    teacher_json = teacher_schema.dump(teacher)
    return {
        "message": APPOINT_ITEM.format(subject_ids, teacher.first_name),
        "data": teacher_json,
    }, 200


@jwt_required()
@find_active_user(TeacherModel, TEACHER, check_jwt=True)
def appoint_student_to_group(
    teacher: TeacherModel, group_id: UUID
) -> Tuple[Dict[str, Any], int]:
    """Allow the Curator of group to appoint students

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
    if not student_ids:
        raise NotProvided(DATA_NOT_PROVIDED("student_ids"))
    group = get_entity_with_teacher(teacher, group_id, GroupModel, GROUP)
    students = get_items(STUDENT, student_ids, StudentModel)
    group.students.extend(students)
    group.save_to_db()
    group_json = group_schema.dump(group)
    return {
        "message": APPOINT_ITEM.format(student_ids, group.name),
        "data": group_json,
    }, 200


@jwt_required()
@find_active_user(TeacherModel, TEACHER, check_jwt=True)
def appoint_subject_to_specialty(
    teacher: TeacherModel, specialty_id: UUID
) -> Tuple[Dict[str, Any], int]:
    """Allow the Head Teacher of specialty to appoint subjects

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
    specialty = get_entity_with_teacher(
        teacher, specialty_id, SpecialtyModel, SPECIALTY
    )
    subjects = get_items(SUBJECT, subject_ids, SubjectModel)
    specialty.subjects.extend(subjects)
    specialty.save_to_db()
    specialty_json = specialty_schema.dump(specialty)
    return {
        "message": APPOINT_ITEM.format(subject_ids, specialty.name),
        "data": specialty_json,
    }, 200


@jwt_required()
@find_active_user(TeacherModel, TEACHER, check_jwt=True)
def appoint_subject_to_group(
    teacher: TeacherModel, group_id: UUID
) -> Tuple[Dict[str, Any], int]:
    """Allow the Curator of group to appoint subjects to group

    :param teacher: an object of existing teacher,
     received from @find_active_user by a UUID from url
    :type teacher: TeacherModel
    :param group_id: UUID of Group from url
    :type group_id: UUID
    :return: Tuple with a dictionary that contains 'message' and
     "data" of the appointed items and status code for the Response
    """
    data = request.get_json()
    subject_ids = data.get("subject_ids", None)
    group = get_entity_with_teacher(teacher, group_id, GroupModel, GROUP)
    subjects = get_items(SUBJECT, subject_ids, SubjectModel)
    group.subjects.extend(subjects)
    group.save_to_db()
    group_json = group_schema.dump(group)
    return {
        "message": APPOINT_ITEM.format(subject_ids, group.name),
        "data": group_json,
    }, 200


# TODO: add remove endpoints for the many-to-many
