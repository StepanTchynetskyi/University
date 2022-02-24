from sqlalchemy.dialects.postgresql import UUID

from application.db import db
from utils.base_model import BaseModel
from utils.constants import MAX_NAME_LENGTH


class AssignmentModel(BaseModel):
    __tablename__ = "assignment"

    name = db.Column(
        db.String(MAX_NAME_LENGTH),
        nullable=False,
    )
    max_mark = db.Column(db.SmallInteger, nullable=False)
    deadline = db.Column(db.DateTime)
    subject_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("subject.id", ondelete="SET NULL"),
        nullable=False,
    )
    subject = db.relationship(
        "SubjectModel", uselist=False, back_populates="assignments"
    )
