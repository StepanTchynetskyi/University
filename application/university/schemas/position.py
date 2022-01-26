from marshmallow import EXCLUDE
from application.ma import ma
from application.university.models.position import PositionModel


class PositionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PositionModel
        load_instance = True
        unknown = EXCLUDE
        dump_only = ("id",)
