from marshmallow import EXCLUDE, validates, ValidationError
from application.ma import ma
from application.university.models.subject import SubjectModel


class SubjectSchema(ma.SQLAlchemyAutoSchema):
    teachers = ma.Nested("TeacherSchema", many=True)
    specialties = ma.Nested("SpecialtySchema", many=True)
    groups = ma.Nested("GroupSchema", many=True)

    class Meta:
        model = SubjectModel
        load_instance = True
        unknown = EXCLUDE
        dump_only = ("id", "created_on", "updated_on")

    # @validates("position_name")
    # def validate_position_name(self, value):
    #     if len(value) < 2:
    #         raise ValidationError("Too short position name (min 2 symbols)")
