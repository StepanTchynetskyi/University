from marshmallow import EXCLUDE, validates, ValidationError
from application.ma import ma
from subjects.models import SubjectModel


class SubjectSchema(ma.SQLAlchemyAutoSchema):
    teachers = ma.Nested("TeacherSchema", many=True, exclude=("subjects",))
    specialties = ma.Nested("SpecialtySchema", many=True)
    groups = ma.Nested("GroupSchema", many=True)

    class Meta:
        model = SubjectModel
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

    @validates("credits")
    def validate_credits(self, value):
        if value < 0 or value > 12:
            raise ValidationError(
                "Wrong value provided for credits "
                "(credits should be in this interval 0 < year < 12)"
            )
