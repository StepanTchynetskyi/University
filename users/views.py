from typing import Tuple, Dict, Any
from uuid import UUID

from flask import request
from flask_jwt_extended import jwt_required
from subjects import models as subject_models
from groups import models as group_models
from specialties import models as specialty_models
from groups import schemas as group_schemas
from specialties import schemas as specialty_schemas
from users import schemas as user_schemas
from positions import models as position_models
from users import models as user_models
from assignments import schemas
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
    DISAPPOINT_ITEM,
)
from utils.schemas import uuid_list_validator
from utils.utils import (
    get_entity_with_teacher,
)
from utils.custom_exceptions import (
    SearchException,
)
from users.utils.utils import (
    get_items,
    update_specific_user,
    remove_items_from_entity,
)
from users.utils.custom_decorators import process_user_json


user_schema = user_schemas.UserSchema()
student_schema = user_schemas.StudentSchema()
teacher_schema = user_schemas.TeacherSchema()
group_schema = group_schemas.GroupSchema()
specialty_schema = specialty_schemas.SpecialtySchema()
student_uuid_list_schema = uuid_list_validator.StudentsUuidListSchema()
subject_uuid_list_schema = uuid_list_validator.SubjectsUuidListSchemas()


@process_user_json(student_schema, STUDENT, request)
def create_student(
    student: user_models.StudentModel,
) -> Tuple[Dict[str, Any], int]:
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
        for student in user_models.StudentModel.get_all_records()
    ]
    return {"data": {"students": students}}, 200


@find_active_user(STUDENT)
def get_student(
    student: user_models.StudentModel,
) -> Tuple[Dict[str, Any], int]:
    """Shows specific student data

    :param student: an object of existing student,
     received from @find_active_user by a UUID from url
    :type student: StudentModel
    :return: Tuple with a dictionary that contains "data" of the teacher
     and status code for the Response
    """
    return {"data": student_schema.dump(student)}, 200


@jwt_required(fresh=True)
@find_active_user(STUDENT, check_jwt=True)
def update_student(
    student: user_models.StudentModel,
) -> Tuple[Dict[str, Any], int]:
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
@find_active_user(STUDENT, check_jwt=True)
def hard_delete_student(
    student: user_models.StudentModel,
) -> Tuple[Dict[str, Any], int]:
    """Allow the Student to delete account

    :param student: an object of existing student,
     received from @find_active_user by a UUID from url
    :type student: StudentModel
    :return: Tuple with a dictionary that contains "message" and status code
    """
    student.remove_from_db()
    return {"message": SUCCESSFULLY_DELETED.format(STUDENT, student.id)}, 200


@jwt_required(fresh=True)
@find_active_user(STUDENT, check_jwt=True)
def soft_delete_student(
    student: user_models.StudentModel,
) -> Tuple[Dict[str, Any], int]:
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
def create_teacher(
    teacher: user_models.TeacherModel,
) -> Tuple[Dict[str, Any], int]:
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
        for teacher in user_models.TeacherModel.get_all_records()
    ]
    return {"data": {"teachers": teachers}}, 200


@find_active_user(TEACHER)
def get_teacher(
    teacher: user_models.TeacherModel,
) -> Tuple[Dict[str, Any], int]:
    """Shows specific teacher data

    :param teacher: an object of existing teacher,
     received from @find_active_user by a UUID from url
    :type teacher: TeacherModel
    :return: Tuple with a dictionary that contains "data" of the teacher
     and status code for the Response
    """
    return {"data": teacher_schema.dump(teacher)}, 200


@jwt_required(fresh=True)
@find_active_user(TEACHER, check_jwt=True)
def update_teacher(
    teacher: user_models.TeacherModel,
) -> Tuple[Dict[str, Any], int]:
    """Allow the Teacher to update account

    :param teacher: an object of existing teacher,
     received from @find_active_user by a UUID from url
    :type teacher: TeacherModel
    :return: Tuple with a dictionary that contains 'message',
     "data" of the teacher and status code for the Response
    """
    position_id = request.get_json().get("position_id", None)
    if position_id:
        position = position_models.PositionModel.get_by_id(position_id)
        if not position:
            raise SearchException(DOES_NOT_EXIST.format(POSITION, position_id))
    teacher_json = update_specific_user(teacher, teacher_schema, request)
    return {
        "message": UPDATED_SUCCESSFULLY.format(TEACHER, teacher.id),
        "data": teacher_json,
    }, 200


@jwt_required(fresh=True)
@find_active_user(TEACHER, check_jwt=True)
def hard_delete_teacher(
    teacher: user_models.TeacherModel,
) -> Tuple[Dict[str, Any], int]:
    """Allow the Teacher to delete account

    :param teacher: an object of existing teacher,
     received from @find_active_user by a UUID from url
    :type teacher: TeacherModel
    :return: Tuple with a dictionary that contains "message" and status code
    """
    teacher.remove_from_db()
    return {"message": SUCCESSFULLY_DELETED.format(TEACHER, teacher.id)}, 200


@jwt_required(fresh=True)
@find_active_user(TEACHER, check_jwt=True)
def soft_delete_teacher(
    teacher: user_models.TeacherModel,
) -> Tuple[Dict[str, Any], int]:
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
@find_active_user(TEACHER, check_jwt=True)
def appoint_subject_to_teacher(
    teacher: user_models.TeacherModel, subject_id: UUID
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
    subject = subject_models.SubjectModel.get_by_id(subject_id)
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
@find_active_user(TEACHER, check_jwt=True)
def appoint_subjects_to_teacher(
    teacher: user_models.TeacherModel,
) -> Tuple[Dict[str, Any], int]:
    """Allow the Teacher to appoint subjects

    :param teacher: an object of existing teacher,
     received from @find_active_user by a UUID from url
    :type teacher: TeacherModel
    :return: Tuple with a dictionary that contains 'message',
     "data" of the appointed items and status code for the Response
    """
    data = request.get_json()
    subject_ids = subject_uuid_list_schema.load(data)["subject_ids"]
    subjects = get_items(SUBJECT, subject_ids, subject_models.SubjectModel)
    teacher.subjects.extend(subjects)
    teacher.save_to_db()
    teacher_json = teacher_schema.dump(teacher)
    return {
        "message": APPOINT_ITEM.format(subject_ids, teacher.first_name),
        "data": teacher_json,
    }, 200


@jwt_required()
@find_active_user(TEACHER, check_jwt=True)
def appoint_student_to_group(
    teacher: user_models.TeacherModel, group_id: UUID
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
    student_ids = student_uuid_list_schema.load(data)["student_ids"]
    group = get_entity_with_teacher(
        teacher, group_id, group_models.GroupModel, GROUP
    )
    students = get_items(STUDENT, student_ids, user_models.StudentModel)
    group.students.extend(students)
    group.save_to_db()
    group_json = group_schema.dump(group)
    return {
        "message": APPOINT_ITEM.format(student_ids, group.name),
        "data": group_json,
    }, 200


@jwt_required()
@find_active_user(TEACHER, check_jwt=True)
def appoint_subject_to_specialty(
    teacher: user_models.TeacherModel, specialty_id: UUID
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
    subject_ids = subject_uuid_list_schema.load(data)["subject_ids"]
    specialty = get_entity_with_teacher(
        teacher, specialty_id, specialty_models.SpecialtyModel, SPECIALTY
    )
    subjects = get_items(SUBJECT, subject_ids, subject_models.SubjectModel)
    specialty.subjects.extend(subjects)
    specialty.save_to_db()
    specialty_json = specialty_schema.dump(specialty)
    return {
        "message": APPOINT_ITEM.format(subject_ids, specialty.name),
        "data": specialty_json,
    }, 200


@jwt_required()
@find_active_user(TEACHER, check_jwt=True)
def appoint_subject_to_group(
    teacher: user_models.TeacherModel, group_id: UUID
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
    subject_ids = subject_uuid_list_schema.load(data)["subject_ids"]
    group = get_entity_with_teacher(
        teacher, group_id, group_models.GroupModel, GROUP
    )
    subjects = get_items(SUBJECT, subject_ids, subject_models.SubjectModel)
    group.subjects.extend(subjects)
    group.save_to_db()
    group_json = group_schema.dump(group)
    return {
        "message": APPOINT_ITEM.format(subject_ids, group.name),
        "data": group_json,
    }, 200


# TODO: add remove endpoints for the many-to-many


@jwt_required()
@find_active_user(TEACHER, check_jwt=True)
def remove_subject_from_teacher(
    teacher: user_models.TeacherModel, subject_id: UUID
) -> Tuple[Dict[str, Any], int]:
    """Allow the Teacher to disappoint specific subject

    :param teacher: an object of existing teacher,
     received from @find_active_user by a UUID from url
    :type teacher: TeacherModel
    :param subject_id: UUID of Subject from url
    :type subject_id: UUID
    :return: Tuple with a dictionary that contains 'message',
    of the disappointed item, "data" of the present state and status code for the Response
    """
    subject = subject_models.SubjectModel.get_by_id(subject_id)
    if not subject:
        raise SearchException(
            NOT_FOUND_BY_ID.format(SUBJECT, subject_id), status_code=400
        )
    remove_items_from_entity(
        teacher.subjects, TEACHER, teacher.id, [subject], SUBJECT
    )
    teacher.save_to_db()
    teacher_json = teacher_schema.dump(teacher)
    return {
        "message": DISAPPOINT_ITEM.format(subject.name, teacher.first_name),
        "data": teacher_json,
    }, 200


@jwt_required()
@find_active_user(TEACHER, check_jwt=True)
def remove_subjects_from_teacher(
    teacher: user_models.TeacherModel,
) -> Tuple[Dict[str, Any], int]:
    """Allow the Teacher to disappoint subjects

    :param teacher: an object of existing teacher,
     received from @find_active_user by a UUID from url
    :type teacher: TeacherModel
    :return: Tuple with a dictionary that contains 'message' of the disappointed items,
     "data" of the present state and status code for the Response
    """
    data = request.get_json()
    subject_ids = subject_uuid_list_schema.load(data)["subject_ids"]
    subjects = get_items(SUBJECT, subject_ids, subject_models.SubjectModel)
    remove_items_from_entity(
        teacher.subjects, TEACHER, teacher.id, subjects, SUBJECT
    )
    teacher.save_to_db()
    teacher_json = teacher_schema.dump(teacher)
    return {
        "message": DISAPPOINT_ITEM.format(subject_ids, teacher.first_name),
        "data": teacher_json,
    }, 200


@jwt_required()
@find_active_user(TEACHER, check_jwt=True)
def remove_student_from_group(
    teacher: user_models.TeacherModel, group_id: UUID
) -> Tuple[Dict[str, Any], int]:
    """Allow the Curator of group to disappoint students

    :param teacher: an object of existing teacher,
     received from @find_active_user by a UUID from url
    :type teacher: TeacherModel
    :param group_id: UUID of Specialty from url
    :type group_id: UUID
    :return: Tuple with a dictionary that contains 'message' and
    of the disappointed items, "data" of the present state and status code for the Response
    """
    data = request.get_json()
    student_ids = student_uuid_list_schema.load(data)["student_ids"]
    group = get_entity_with_teacher(
        teacher, group_id, group_models.GroupModel, GROUP
    )
    students = get_items(STUDENT, student_ids, user_models.StudentModel)
    remove_items_from_entity(
        group.students, GROUP, group.id, students, STUDENT
    )
    group.save_to_db()
    group_json = group_schema.dump(group)
    return {
        "message": DISAPPOINT_ITEM.format(student_ids, group.name),
        "data": group_json,
    }, 200


@jwt_required()
@find_active_user(TEACHER, check_jwt=True)
def remove_subject_from_specialty(
    teacher: user_models.TeacherModel, specialty_id: UUID
) -> Tuple[Dict[str, Any], int]:
    """Allow the Head Teacher of specialty to disappoint subjects

    :param teacher: an object of existing teacher,
     received from @find_active_user by a UUID from url
    :type teacher: TeacherModel
    :param specialty_id: UUID of Specialty from url
    :type specialty_id: UUID
    :return: Tuple with a dictionary that contains 'message' and
     of the disappointed items, "data" of the present state and status code for the Response
    """
    data = request.get_json()
    subject_ids = subject_uuid_list_schema.load(data)["subject_ids"]
    specialty = get_entity_with_teacher(
        teacher, specialty_id, specialty_models.SpecialtyModel, SPECIALTY
    )
    subjects = get_items(SUBJECT, subject_ids, subject_models.SubjectModel)
    remove_items_from_entity(
        specialty.subjects, SPECIALTY, specialty.id, subjects, SUBJECT
    )
    specialty.save_to_db()
    specialty_json = specialty_schema.dump(specialty)
    return {
        "message": DISAPPOINT_ITEM.format(subject_ids, specialty.name),
        "data": specialty_json,
    }, 200


@jwt_required()
@find_active_user(TEACHER, check_jwt=True)
def remove_subject_from_group(
    teacher: user_models.TeacherModel, group_id: UUID
) -> Tuple[Dict[str, Any], int]:
    """Allow the Curator of group to disappoint subjects from group

    :param teacher: an object of existing teacher,
     received from @find_active_user by a UUID from url
    :type teacher: TeacherModel
    :param group_id: UUID of Group from url
    :type group_id: UUID
    :return: Tuple with a dictionary that contains 'message'
     of the disappointed items, "data" of the present state and status code for the Response
    """
    data = request.get_json()
    subject_ids = subject_uuid_list_schema.load(data)["subject_ids"]
    group = get_entity_with_teacher(
        teacher, group_id, group_models.GroupModel, GROUP
    )
    subjects = get_items(SUBJECT, subject_ids, subject_models.SubjectModel)
    remove_items_from_entity(
        group.subjects, GROUP, group.id, subjects, SUBJECT
    )
    group.save_to_db()
    group_json = group_schema.dump(group)
    return {
        "message": DISAPPOINT_ITEM.format(subject_ids, group.name),
        "data": group_json,
    }, 200
