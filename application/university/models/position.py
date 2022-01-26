import uuid

from sqlalchemy.dialects.postgresql import UUID

from application import db
from application.university.utils.constants import MAX_POSITION_LENGTH


class PositionModel(db.Model):
    __tablename__ = "position"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    position_name = db.Column(db.String(MAX_POSITION_LENGTH), nullable=False)
    teacher = db.relationship("TeacherModel", backref="position")

    @classmethod
    def find_by_id(cls, position_id):
        return cls.query.filter_by(id=position_id).first()

    @classmethod
    def find_by_name(cls, position_name):
        return cls.query.filter_by(position_name=position_name).first()
