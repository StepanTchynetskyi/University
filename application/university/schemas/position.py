from marshmallow import EXCLUDE, validates, ValidationError
from application.ma import ma
from application.university.models.position import PositionModel


class PositionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PositionModel
        load_instance = True
        unknown = EXCLUDE
        dump_only = ("id",)

    @validates("position_name")
    def validate_position_name(self, value):
        if len(value) < 2:
            raise ValidationError("Too short position name (min 2 symbols)")
