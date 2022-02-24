import uuid

from flask import request
from flask_jwt_extended import jwt_required

from assignments import schemas as assignment_schemas
from assignments.utils.utils import (
    get_assignment_from_subject,
    check_name_accessibility,
)
from subjects import models as subject_models
from users import models as user_models
from utils.constants import (
    SUBJECT,
    CREATED_SUCCESSFULLY,
    ASSIGNMENT,
    IMPOSSIBLE_TO_UPDATE,
    UPDATED_SUCCESSFULLY,
    SUCCESSFULLY_DELETED,
    TEACHER,
)
from utils.custom_decorators import find_active_user
from utils.custom_exceptions import UpdateException
from utils.utils import get_entity, get_entity_with_teacher

assignment_schema = assignment_schemas.AssignmentSchema()
# TODO: rework logic with teacher_id


@jwt_required(fresh=True)
@find_active_user(TEACHER, check_jwt=True)
def create_assignment(
    teacher: user_models.TeacherModel, subject_id: uuid.UUID
):
    subject = get_entity_with_teacher(
        teacher, subject_id, subject_models.SubjectModel, SUBJECT
    )
    assignment_json = request.get_json()
    assignment_json["subject_id"] = subject.id
    assignment = assignment_schema.load(assignment_json)
    check_name_accessibility(subject, assignment.name)
    assignment.save_to_db()
    assignment_json = assignment_schema.dump(assignment)
    return {
        "message": CREATED_SUCCESSFULLY.format(ASSIGNMENT, assignment.id),
        "data": assignment_json,
    }, 201


def get_assignments(subject_id: uuid.UUID):
    subject = get_entity(subject_id, subject_models.SubjectModel, SUBJECT)
    assignments = [
        assignment_schema.dump(assignment)
        for assignment in subject.assignments
    ]
    return {"data": {"assignments": assignments}}, 200


def get_assignment(subject_id: uuid.UUID, assignment_id: uuid.UUID):
    subject = get_entity(subject_id, subject_models.SubjectModel, SUBJECT)
    assignment = get_assignment_from_subject(subject, assignment_id)
    assignment_json = assignment_schema.dump(assignment)
    return {"data": assignment_json}, 200


@jwt_required(fresh=True)
@find_active_user(TEACHER, check_jwt=True)
def update_assignment(
    teacher: user_models.TeacherModel,
    subject_id: uuid.UUID,
    assignment_id: uuid.UUID,
):
    subject = get_entity_with_teacher(
        teacher, subject_id, subject_models.SubjectModel, SUBJECT
    )
    assignment_obj = get_assignment_from_subject(subject, assignment_id)
    assignment_json = request.get_json()
    if "subject_id" in assignment_json:
        raise UpdateException(IMPOSSIBLE_TO_UPDATE.format("subject_id"))
    assignment_name = assignment_json.get("name", None)
    if assignment_name:
        check_name_accessibility(subject, assignment_name)
    assignment = assignment_schema.load(
        assignment_json, instance=assignment_obj, partial=True
    )
    assignment.save_to_db()
    assignment_json = assignment_schema.dump(assignment)
    return {
        "message": UPDATED_SUCCESSFULLY.format(ASSIGNMENT, assignment_id),
        "data": assignment_json,
    }, 200


@jwt_required(fresh=True)
@find_active_user(TEACHER, check_jwt=True)
def delete_assignment(
    teacher: user_models.TeacherModel,
    subject_id: uuid.UUID,
    assignment_id: uuid.UUID,
):
    subject = get_entity_with_teacher(
        teacher, subject_id, subject_models.SubjectModel, SUBJECT
    )
    assignment_obj = get_assignment_from_subject(subject, assignment_id)
    assignment_obj.remove_from_db()
    return {
        "message": SUCCESSFULLY_DELETED.format(ASSIGNMENT, assignment_id)
    }, 200
