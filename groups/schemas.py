from marshmallow import EXCLUDE, validates, ValidationError
from application.ma import ma
from groups import models as group_models


class GroupSchema(ma.SQLAlchemyAutoSchema):
    specialty = ma.Nested(
        "SpecialtySchema",
        many=False,
        exclude=("groups", "teacher_id", "subjects"),
    )

    students = ma.Nested("StudentSchema", many=True, exclude=("groups",))
    subjects = ma.Nested(
        "SubjectSchema", many=True, exclude=("groups", "specialties")
    )

    class Meta:
        model = group_models.GroupModel
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

    @validates("credits_per_student")
    def validate_credits_per_student(self, value):
        if value < 0 or value > 150:
            raise ValidationError(
                "Wrong value provided for credits_per_student "
                "(credits_per_student should be in this interval 0 < year < 150)"
            )
