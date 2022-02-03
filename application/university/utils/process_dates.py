from marshmallow import ValidationError

from application.university.utils.constants import ALREADY_EXISTS_WITH_YEAR
from application.university.utils.custom_exceptions import SearchException


def check_accessibility_for_name_and_year(
    subject, subject_json, model, checked_entity
):
    year = subject_json.get("year", None)
    name = subject_json.get("name", None)
    if year or name:
        year, name = year or subject.year, name or subject.name
        if isinstance(year, int):
            searched_obj = model.get_by_name_and_year(name, year)
            if searched_obj:
                raise SearchException(
                    ALREADY_EXISTS_WITH_YEAR.format(
                        checked_entity,
                        searched_obj.name,
                        searched_obj.year,
                        400,
                    )
                )
        else:
            raise ValidationError({"year": "Not a valid integer"})
