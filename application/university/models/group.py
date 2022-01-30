from sqlalchemy.dialects.postgresql import UUID

from application.db import db
from application.university.utils.constants import MAX_NAME_LENGTH
from application.university.utils.base_model import BaseModel


class GroupModel(BaseModel):
    __tablename__ = "group"

    name = db.Column(db.String(MAX_NAME_LENGTH), nullable=False)
    group_date = db.Column(
        db.Date, nullable=False
    )  # probably overhead as created_on could replace it
    credits_per_student = db.Column(db.SmallInteger, nullable=False)
    curator_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("teacher.id", ondelete="SET NULL")
    )
    specialty_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("specialty.id", ondelete="SET NULL")
    )


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
