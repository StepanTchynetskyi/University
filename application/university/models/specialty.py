from sqlalchemy.dialects.postgresql import UUID

from application.db import db
from application.university.utils.constants import MAX_NAME_LENGTH
from application.university.utils.base_model import BaseModel


class SpecialtyModel(BaseModel):
    __tablename__ = "specialty"

    name = db.Column(db.String(MAX_NAME_LENGTH), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    teacher_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("teacher.id", ondelete="SET NULL")
    )
    group = db.relationship("GroupModel", uselist=False, backref="specialty")

    @classmethod
    def get_by_name_and_year(cls, name, year):
        return cls.query.filter_by(name=name, year=year).first()

    @classmethod
    def get_by_year(cls, year):
        return cls.query.filter_by(year=year).first()
