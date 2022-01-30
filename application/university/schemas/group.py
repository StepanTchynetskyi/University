from marshmallow import EXCLUDE, validates, ValidationError
from application.ma import ma
from application.university.models.group import GroupModel


class GroupSchema(ma.SQLAlchemyAutoSchema):
    specialty = ma.Nested("SpecialtySchema", many=False)

    students = ma.Nested("StudentSchema", many=True)
    subjects = ma.Nested("SubjectSchema", many=True)

    class Meta:
        model = GroupModel
        load_instance = True
        unknown = EXCLUDE
        dump_only = ("id", "created_on", "updated_on")

    # @validates("name")
    # def validate_position_name(self, value):
    #     if len(value) < 2:
    #         raise ValidationError("Too short position name (min 2 symbols)")
