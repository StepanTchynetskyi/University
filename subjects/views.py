from flask import request
from flask_jwt_extended import jwt_required

from subjects import schemas as subject_schemas
from subjects import models as subject_models
from utils.constants import (
    CREATED_SUCCESSFULLY,
    SUBJECT,
    NOT_FOUND_BY_ID,
    UPDATED_SUCCESSFULLY,
    SUCCESSFULLY_DELETED,
    TEACHER,
)
from utils.custom_decorators import (
    create_obj_with_name_and_year,
    find_active_user,
)
from utils.custom_exceptions import SearchException
from utils.utils import (
    get_item_from_entity,
    check_accessibility_for_name_and_year,
)

subject_schema = subject_schemas.SubjectSchema()


@jwt_required(fresh=True)
@find_active_user(TEACHER, check_jwt=True)
@create_obj_with_name_and_year(
    subject_models.SubjectModel, SUBJECT, subject_schema, request
)
def create_subject(subject, subject_json, teacher):
    subject.save_to_db()
    teacher.subjects.append(subject)
    teacher.save_to_db()
    return {
        "message": CREATED_SUCCESSFULLY.format(SUBJECT, subject.id),
        "data": subject_json,
    }, 201


def get_subjects():
    subjects = [
        subject_schema.dump(subject)
        for subject in subject_models.SubjectModel.get_all_records()
    ]
    return {"data": {"subjects": subjects}}, 200


@find_active_user(TEACHER)
def get_teacher_subjects(teacher):
    subjects = [subject_schema.dump(subject) for subject in teacher.subjects]
    return {
        "message": "{} for {} <id={}>".format("Subjects", TEACHER, teacher.id),
        "data": {"subjects": subjects},
    }, 200


def get_subject(subject_id):
    subject = subject_models.SubjectModel.get_by_id(subject_id)
    if not subject:
        raise SearchException(NOT_FOUND_BY_ID.format(SUBJECT, subject_id))
    return {"data": subject_schema.dump(subject)}, 200


@find_active_user(TEACHER)
def get_teacher_subject(teacher, subject_id):
    subject = get_item_from_entity(
        teacher.id, teacher.subjects, subject_id, TEACHER, SUBJECT
    )
    return {
        "message": "{} for {} <id={}>".format(SUBJECT, TEACHER, teacher.id),
        "data": subject_schema.dump(subject),
    }, 200


@jwt_required(fresh=True)
@find_active_user(TEACHER)
def update_subject(teacher, subject_id):
    subject_json = request.get_json()
    subject = get_item_from_entity(
        teacher.id, teacher.subjects, subject_id, TEACHER, SUBJECT
    )
    subject = subject_schema.load(subject_json, instance=subject, partial=True)
    check_accessibility_for_name_and_year(
        subject, subject_json, subject_models.SubjectModel, SUBJECT
    )
    subject.save_to_db()
    subject_json = subject_schema.dump(subject)
    return {
        "message": UPDATED_SUCCESSFULLY.format(SUBJECT, subject_id),
        "data": subject_json,
    }, 200


@jwt_required(fresh=True)
@find_active_user(TEACHER)
def delete_subject(teacher, subject_id):
    subject = get_item_from_entity(
        teacher.id, teacher.subjects, subject_id, TEACHER, SUBJECT
    )
    subject.remove_from_db()
    return {"message": SUCCESSFULLY_DELETED.format(SUBJECT, subject_id)}, 200
