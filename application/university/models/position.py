from application.db import db
from application.university.utils.constants import MAX_NAME_LENGTH
from application.university.utils.base_model import BaseModel


class PositionModel(BaseModel):
    __tablename__ = "position"

    position_name = db.Column(
        db.String(MAX_NAME_LENGTH), nullable=False, unique=True
    )
    teacher = db.relationship("TeacherModel", backref="position")

    @classmethod
    def get_by_position_name(cls, position_name):
        return cls.query.filter_by(position_name=position_name).first()
