from sqlalchemy.dialects.postgresql import UUID


from application.db import db
from application.university.utils.constants import MAX_NAME_LENGTH
from application.university.utils.base_model import BaseModel


class SubjectModel(BaseModel):
    __tablename__ = "subject"

    name = db.Column(db.String(MAX_NAME_LENGTH), nullable=False)
    subject_date = db.Column(
        db.Date, nullable=False
    )  # probably overhead as created_on could replace it
    credits = db.Column(db.SmallInteger, nullable=False)


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
