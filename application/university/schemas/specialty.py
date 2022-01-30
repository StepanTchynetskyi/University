import datetime

from marshmallow import EXCLUDE, validates, ValidationError
from application.ma import ma
from application.university.models.specialty import SpecialtyModel


class SpecialtySchema(ma.SQLAlchemyAutoSchema):
    teacher = ma.Nested("TeacherSchema", many=False)

    groups = ma.Nested("GroupSchema", many=True)
    subjects = ma.Nested("SubjectSchema", many=True)

    class Meta:
        model = SpecialtyModel
        load_instance = True
        unknown = EXCLUDE
        dump_only = ("id", "created_on", "updated_on")

    @validates("name")
    def validate_name(self, value):
        if len(value) < 2:
            raise ValidationError("Too short name (min 2 symbols)")

    # @validates("specialty_date")
    # def validate_name(self, value):
    #     print(value)
    #     date_difference = value.year - datetime.datetime.year
    #     if date_difference > 1 or date_difference < -1:
    #         raise ValidationError("Wrong date provided")  # message should be changed
