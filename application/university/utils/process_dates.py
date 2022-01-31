from marshmallow import ValidationError

from application.university.utils.constants import ALREADY_EXISTS_WITH_YEAR
from application.university.utils.custom_exceptions import SearchException


def check_year(model, year, name, searched_entity):
    if isinstance(year, int):
        searched_obj = model.get_by_name_and_year(name, year)
        if searched_obj:
            raise SearchException(
                ALREADY_EXISTS_WITH_YEAR.format(
                    searched_entity, searched_obj.name, searched_obj.year, 400
                )
            )
    else:
        raise ValidationError("year: Not a valid integer")
