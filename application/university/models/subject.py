from sqlalchemy.dialects.postgresql import UUID


from application.db import db
from application.university.utils.constants import MAX_NAME_LENGTH
from application.university.utils.base_model import BaseModel


subject_specialty = db.Table(
    "subject_specialty",
    db.Column(
        "subject_id",
        UUID(as_uuid=True),
        db.ForeignKey("subject.id"),
        primary_key=True,
    ),
    db.Column(
        "specialty_id",
        UUID(as_uuid=True),
        db.ForeignKey("specialty.id"),
        primary_key=True,
    ),
)

subject_teacher = db.Table(
    "subject_teacher",
    db.Column(
        "subject_id",
        UUID(as_uuid=True),
        db.ForeignKey("subject.id"),
        primary_key=True,
    ),
    db.Column(
        "teacher_id",
        UUID(as_uuid=True),
        db.ForeignKey("teacher.id"),
        primary_key=True,
    ),
)

subject_group = db.Table(
    "subject_group",
    db.Column(
        "subject_id",
        UUID(as_uuid=True),
        db.ForeignKey("subject.id"),
        primary_key=True,
    ),
    db.Column(
        "group_id",
        UUID(as_uuid=True),
        db.ForeignKey("group.id"),
        primary_key=True,
    ),
)


class SubjectModel(BaseModel):
    __tablename__ = "subject"

    name = db.Column(db.String(MAX_NAME_LENGTH), nullable=False)
    year = db.Column(
        db.Integer, nullable=False
    )  # probably overhead as created_on could replace it
    credits = db.Column(db.SmallInteger, nullable=False)
    specialties = db.relationship(
        "SpecialtyModel",
        secondary=subject_specialty,
        lazy="subquery",
        backref=db.backref("subjects", lazy=True),
    )
    teachers = db.relationship(
        "TeacherModel",
        secondary=subject_teacher,
        lazy="subquery",
        backref=db.backref("subjects", lazy=True),
    )
    groups = db.relationship(
        "GroupModel",
        secondary=subject_group,
        lazy="subquery",
        backref=db.backref("subjects", lazy=True),
    )

    @classmethod
    def get_by_name_and_year(cls, name, year):
        return cls.query.filter_by(name=name, year=year).first()

    @classmethod
    def get_by_year(cls, year):
        return cls.query.filter_by(year=year).first()
