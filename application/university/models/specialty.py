from sqlalchemy.dialects.postgresql import UUID

from application.db import db
from application.university.utils.constants import MAX_NAME_LENGTH
from application.university.utils.base_model import BaseModel


class SpecialtyModel(BaseModel):
    __tablename__ = "specialty"

    name = db.Column(db.String(MAX_NAME_LENGTH), nullable=False)
    specialty_date = db.Column(
        db.Date, nullable=False
    )  # probably overhead as created_on could replace it
    teacher_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("teacher.id", ondelete="SET NULL")
    )
