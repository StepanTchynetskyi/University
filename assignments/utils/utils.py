from utils.constants import (
    ASSIGNMENT_NOT_FOUND_IN_SUBJECT,
    ASSIGNMENT,
    ALREADY_EXISTS,
)
from utils.custom_exceptions import SearchException, CreateException


def get_assignment_from_subject(subject, assignment_id):
    for assignment in subject.assignments:
        if str(assignment.id) == str(assignment_id):
            return assignment
    else:
        raise SearchException(
            ASSIGNMENT_NOT_FOUND_IN_SUBJECT.format(assignment_id, subject.id)
        )


def check_name_accessibility(subject, name):
    for assignment_item in subject.assignments:
        if assignment_item.name == name:
            raise CreateException(
                ALREADY_EXISTS.format(ASSIGNMENT, assignment_item.name)
            )
