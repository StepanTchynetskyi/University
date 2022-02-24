import datetime

from marshmallow import EXCLUDE, validates, ValidationError
from application.ma import ma
from assignments import models as assignment_models


class AssignmentSchema(ma.SQLAlchemyAutoSchema):
    subject = ma.Nested("SubjectSchema", many=False)

    class Meta:
        model = assignment_models.AssignmentModel
        load_instance = True
        unknown = EXCLUDE
        dump_only = ("id", "created_on", "updated_on")
        include_fk = True

    @validates("name")
    def validate_name(self, value):
        if len(value) < 2:
            raise ValidationError("Too short name (min 2 symbols)")

    @validates("max_mark")
    def validate_max_mark(self, value):
        if value < 1:
            raise ValidationError(
                "Max mark should be greater than or equal to 1"
            )
        if value > 100:
            raise ValidationError(
                "Max mark should be less than or equal to 100"
            )

    @validates("deadline")
    def validate_deadline(self, value):
        if value < datetime.datetime.now():
            raise ValidationError(
                "Wrong deadline provided, it is not possible to set a deadline for the past"
            )
