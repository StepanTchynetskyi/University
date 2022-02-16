from flask import request

from subjects.schemas import SubjectSchema
from subjects.models import SubjectModel
from utils.constants import (
    CREATED_SUCCESSFULLY,
    SUBJECT,
    NOT_FOUND_BY_ID,
    UPDATED_SUCCESSFULLY,
    SUCCESSFULLY_DELETED,
    EntityInfo,
)
from utils.custom_decorators import (
    create_obj_with_name_and_year,
)
from utils.utils import update_obj_with_name_and_year


subject_schema = SubjectSchema()


@create_obj_with_name_and_year(SubjectModel, SUBJECT, subject_schema, request)
def create_subject(subject, subject_json):
    subject.save_to_db()
    return {
        "message": CREATED_SUCCESSFULLY.format(SUBJECT, subject.id),
        "data": subject_json,
    }, 201


def get_subjects():
    subjects = [
        subject_schema.dump(subject)
        for subject in SubjectModel.get_all_records()
    ]
    return {"data": subjects}, 200


def get_subject(subject_id):
    subject = SubjectModel.get_by_id(subject_id)
    if not subject:
        return {"message": NOT_FOUND_BY_ID.format(SUBJECT, subject_id)}, 400
    return {"data": subject_schema.dump(subject)}, 200


def update_subject(subject_id):
    subject_info = EntityInfo(
        subject_id, SubjectModel, subject_schema, SUBJECT
    )
    subject_json = update_obj_with_name_and_year(subject_info, request)
    return {
        "message": UPDATED_SUCCESSFULLY.format(SUBJECT, subject_id),
        "data": subject_json,
    }, 200


def delete_subject(subject_id):
    subject = SubjectModel.get_by_id(subject_id)
    if not subject:
        return {"message": NOT_FOUND_BY_ID.format(SUBJECT, subject_id)}, 400
    subject.remove_from_db()
    return {"message": SUCCESSFULLY_DELETED.format(SUBJECT, subject_id)}, 200
