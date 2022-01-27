import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import exc

from application import db
from application.university.utils.constants import MAX_POSITION_NAME_LENGTH


class PositionModel(db.Model):
    __tablename__ = "position"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    position_name = db.Column(
        db.String(MAX_POSITION_NAME_LENGTH), nullable=False, unique=True
    )
    teacher = db.relationship("TeacherModel", backref="position")

    def save_to_db(self):
        db.session.add(self)
        try:
            db.session.commit()
        except exc.SQLAlchemyError as err:
            db.session.rollback()
            return str(err)
        return False

    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, position_id):
        return cls.query.filter_by(id=position_id).first()

    @classmethod
    def get_by_position_name(cls, position_name):
        return cls.query.filter_by(position_name=position_name).first()

    @classmethod
    def get_all_positions(cls):
        return cls.query.all()
