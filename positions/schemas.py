from marshmallow import EXCLUDE, validates, ValidationError
from application.ma import ma
from positions import models as position_models


class PositionSchema(ma.SQLAlchemyAutoSchema):
    teachers = ma.Nested("TeacherSchema", many=True, exclude=("position",))

    class Meta:
        model = position_models.PositionModel
        load_instance = True
        unknown = EXCLUDE
        dump_only = ("id", "created_on", "updated_on")
        include_fk = True

    @validates("position_name")
    def validate_position_name(self, value):
        if len(value) < 2:
            raise ValidationError("Too short position name (min 2 symbols)")
