from sqlalchemy.dialects.postgresql import UUID

from application.db import db
from utils.constants import MAX_NAME_LENGTH
from utils.base_model import BaseModel

group_student = db.Table(
    "group_student",
    db.Column(
        "group_id",
        UUID(as_uuid=True),
        db.ForeignKey("group.id"),
        primary_key=True,
    ),
    db.Column(
        "student_id",
        UUID(as_uuid=True),
        db.ForeignKey("student.id"),
        primary_key=True,
    ),
)


class GroupModel(BaseModel):
    __tablename__ = "group"

    name = db.Column(db.String(MAX_NAME_LENGTH), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    credits_per_student = db.Column(db.SmallInteger, nullable=False)
    curator_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("teacher.id", ondelete="SET NULL")
    )
    specialty_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("specialty.id", ondelete="SET NULL")
    )
    students = db.relationship(
        "StudentModel",
        secondary=group_student,
        lazy="subquery",
        backref=db.backref("groups", lazy=True),
    )
    specialty = db.relationship(
        "SpecialtyModel", uselist=False, back_populates="groups"
    )

    @classmethod
    def get_by_name_and_year(cls, name, year):
        return cls.query.filter_by(name=name, year=year).first()

    @classmethod
    def get_by_year(cls, year):
        return cls.query.filter_by(year=year).first()
