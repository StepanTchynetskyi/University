from marshmallow import EXCLUDE, validates, ValidationError
from application.ma import ma
from application.university.models.specialty import SpecialtyModel


class SpecialtySchema(ma.SQLAlchemyAutoSchema):
    teacher = ma.Nested("TeacherSchema", many=False, exclude=("specialty",))

    groups = ma.Nested("GroupSchema", many=True, exclude=("specialty",))
    subjects = ma.Nested("SubjectSchema", many=True)

    class Meta:
        model = SpecialtyModel
        load_instance = True
        unknown = EXCLUDE
        dump_only = ("id", "created_on", "updated_on")
        include_fk = True

    @validates("name")
    def validate_name(self, value):
        if len(value) < 2:
            raise ValidationError("Too short name (min 2 symbols)")

    @validates("year")
    def validate_year(self, value):
        if value < 1088 or value > 10000:
            raise ValidationError(
                "Wrong year provided (year should be in this interval 1088 < year < 10000)"
            )
